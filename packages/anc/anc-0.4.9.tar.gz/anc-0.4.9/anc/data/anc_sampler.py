from torch.utils.data.sampler import *
from torch.utils.data.distributed import DistributedSampler
import random
import time
import math
import copy

class CustomizedRange:
    def __init__(self, start, end, seed=0):
        self.start = start
        self.end = end
        self.seed = seed
        self.random = random.Random(seed)

    def __len__(self):
        return self.end - self.start

    def clone(self, clone_times=1):
        return CustomizedRange(self.start, self.end, self.seed + clone_times)

    def to_list(self, shuffle=False):
        lst = list(range(self.start, self.end))
        if shuffle:
            self.random.shuffle(lst)
        return lst

    def split_to_lists(self, chunk_sizes, shuffle=False):
        lst = self.to_list(shuffle)
        chunks = []
        assert sum(chunk_sizes) == self.end - self.start
        accu_length = 0
        for chunk_size in chunk_sizes:
            chunks.append(lst[accu_length: accu_length + chunk_size])
            accu_length += chunk_size
        return chunks

    def slice(self, start, length):
        assert start + self.start + length <= self.end
        return CustomizedRange(start + self.start, start + self.start + length, self.seed)


class RangesHolder:
    def __init__(self, list_of_ranges):
        self.list_of_ranges = list_of_ranges
        self.length = sum(len(r) for r in list_of_ranges)
        self.expanded = {}
    
    def __len__(self):
        return self.length

    def get_start_and_end_ranges(self, start, length):
        start_range_id, start_range_offset = 0, 0
        accu_length = 0
        end = start + length
        end_range_id = len(self.list_of_ranges) - 1
        end_range_offset = len(self.list_of_ranges[end_range_id])
        for i in range(len(self.list_of_ranges)):
            if start < accu_length + len(self.list_of_ranges[i]):
                start_range_id = i
                start_range_offset = start - accu_length
                break
            accu_length += len(self.list_of_ranges[i])
        for i in range(start_range_id, len(self.list_of_ranges)):
            accu_length += len(self.list_of_ranges[i])
            if end < accu_length:
                end_range_id = i
                end_range_offset = end - (accu_length - len(self.list_of_ranges[i]))
                break
        return start_range_id, start_range_offset, end_range_id, end_range_offset

    def slice(self, start, length):
        start_range_id, start_range_offset, end_range_id, end_range_offset = self.get_start_and_end_ranges(start, length)
        res = []
        for i in range(start_range_id, end_range_id + 1):
            if i == start_range_id:
                if start_range_id == end_range_id:
                    res.append(self.list_of_ranges[i].slice(start_range_offset, end_range_offset - start_range_offset))
                else:
                    res.append(self.list_of_ranges[i].slice(start_range_offset, len(self.list_of_ranges[i]) - start_range_offset))
            elif i == end_range_id:
                res.append(self.list_of_ranges[i].slice(0, end_range_offset))
            else:
                res.append(self.list_of_ranges[i])
        target = RangesHolder(res)
        assert target.length == length
        return target
    
    def combine(self, other):
        for i in other.list_of_ranges:
            self.list_of_ranges.append(i)
        self.length = sum(len(r) for r in self.list_of_ranges)

    def to_list(self, shuffle=False):
        res = []
        for rng in self.list_of_ranges:
            res += rng.to_list(shuffle)
        return res

    def expand(self, range_idx, shuffle=False):
        if range_idx in self.expanded:
            return self.expanded[range_idx]
        else:
            self.expanded[range_idx] = self.list_of_ranges[range_idx].to_list(shuffle)
            return self.expanded[range_idx]

    def get_value_from(self, start, end, shuffle=False):
        start_range_id, start_range_offset, end_range_id, end_range_offset = self.get_start_and_end_ranges(start, end - start)
        res = []
        for range_idx in range(start_range_id, end_range_id + 1):
            indices = self.expand(range_idx, shuffle)
            if range_idx == start_range_id:
                if range_idx == end_range_id:
                    assert start_range_offset + end - start <= len(self.list_of_ranges[range_idx])
                    res = indices[start_range_offset: start_range_offset + end - start]
                else:
                    res += indices[start_range_offset:]
            elif range_idx == end_range_id:
                res += indices[:end_range_offset]
            else:
                res += indices
        return res

    def random_reset(self, idx):
        self.expanded = {}
        self.list_of_ranges = self.list_of_ranges[idx:] + self.list_of_ranges[:idx]

    

class AncSampler(DistributedSampler):
    r'''
    A batch sampler controls the data sharding, data shuffling and data loading order with proper indices

    The data sharding is chunk based. For example, to shard a dataset with 10 elements into 2 splits, 
    the result data index would be [[0,1,2,3,4],[5,6,7,8,9]] instead of [[0,2,4,6,8],[1,3,5,7,9]]

    Args:
        dataset: dataset from which to load the data.
        batch_size (int): how many samples per batch to load.
        world (int, optional): data parallel world size (default: ``1``).
        rank (int, optional): data parallel rank of current process (default: ``0``).
        num_workers (int): how many subprocesses to use for data
            loading. ``0`` means that the data will be loaded in the main process.
        shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``False``).
        drop_last (bool, optional): set to ``True`` to drop the last incomplete batch,
            if the dataset size is not divisible by the batch size. If ``False`` and
            the size of dataset is not divisible by the batch size, then the last batch
            will be smaller. (default: ``False``).
        seed (int, optional): seed for randomness (default: ``0``).
        resume_step (int, optional): the step to resume from, 
            the previous steps will be skipped (default: ``0``).
        repeat (bool, optional): set to ``True`` to repeat the indices when gone through 
            all the data. If ``False`` than StopIteration will be raised when all data 
            is consumed (default: ``False``).
    '''
    def __init__(
        self,
        dataset,
        batch_size,
        world = 1,
        rank = 0,
        num_workers = 1,
        shuffle = False,
        drop_last = False,
        seed = 0,
        resume_step = 0,
        repeat = False,
        global_shuffle = False,
        ratios = [1],
        chunk_granularity = -1,
        mem_save_mode = False,
    ):
        if hasattr(dataset, 'get_sub_lengths'):
            self.sub_lengths = dataset.get_sub_lengths()
        else:
            assert isinstance(dataset, list)
            self.sub_lengths = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.resume_step = resume_step
        self.step = resume_step
        self.seed = seed
        self.last_iter_epoch = -1
        self.indices = None
        self.repeat = repeat
        self.inner_epoch_count = 0
        self.global_shuffle = global_shuffle
        self.num_replicas = world
        self.rank = rank
        self.epoch = 0
        self.drop_last = drop_last
        self.chunk_granularity = chunk_granularity
        self.mem_save_mode = mem_save_mode
        if self.mem_save_mode:
            assert self.chunk_granularity == -1, "chunk_granularity is not supported when mem_save_mode is True"
        if len(ratios) == 1:
            self.ratios = ratios * len(self.sub_lengths)
        else:
            assert len(ratios) == len(self.sub_lengths)
            self.ratios = ratios
        ds_length = 0
        for item, ratio in zip(self.sub_lengths, self.ratios):
            if isinstance(item, list):
                ds_length += math.ceil(sum(item) * ratio)
            else:
                ds_length += math.ceil(item * ratio)
        if self.drop_last and ds_length % self.num_replicas != 0:
            self.num_samples = math.ceil((ds_length - self.num_replicas) / self.num_replicas)
        else:
            self.num_samples = math.ceil(ds_length / self.num_replicas)
        self.total_size = self.num_samples * self.num_replicas
        self.shuffle = shuffle
        if getattr(self, "dataset", None) is not None:
            self.dataset = None

    def _get_indices_with_ratio(self, indices, ratio):
        ratio_int = math.floor(ratio)
        ratio_float = ratio - ratio_int
        res = []
        for ratio_cnt in range(ratio_int):
            if isinstance(indices, CustomizedRange):
                tmp_indices = indices.clone(ratio_cnt)
                res.append(tmp_indices)
            else:
                tmp_indices = indices[:]
                if self.shuffle:
                    random.shuffle(tmp_indices)
                if self.chunk_granularity > 0:
                    num_chunks = (len(tmp_indices) + self.chunk_granularity - 1) // self.chunk_granularity
                    for i in range(num_chunks):
                        res.append(tmp_indices[i * self.chunk_granularity: (i + 1) * self.chunk_granularity])
                else:
                    res.append(tmp_indices)
        if ratio_float > 0:
            if isinstance(indices, CustomizedRange):
                tmp_indices = indices.clone(ratio_int)
                length = math.ceil(ratio_float * len(tmp_indices))
                start = 0 if not self.shuffle else random.randint(0, len(tmp_indices) - length)
                res.append(tmp_indices.slice(start, length))
            else:
                tmp_indices = indices[:]
                if self.shuffle:
                    random.shuffle(tmp_indices)
                tmp_indices = tmp_indices[:math.ceil(ratio_float * len(tmp_indices))]
                if self.chunk_granularity > 0:
                    num_chunks = (len(tmp_indices) + self.chunk_granularity - 1) // self.chunk_granularity
                    for i in range(num_chunks):
                        res.append(tmp_indices[i * self.chunk_granularity: (i + 1) * self.chunk_granularity])
                else:
                    res.append(tmp_indices)
        if self.shuffle:
            random.shuffle(res)
        return res

    def _get_indices(self, sub_lengths, offset=0, return_sub_indices=False, ratio=[1]):
        if self.mem_save_mode:
            assert return_sub_indices is True
        indices_list = []
        random.seed(self.seed)
        accumulate_length = offset
        if len(ratio) == 1:
            ratio = ratio * len(sub_lengths)
        else:
            assert len(ratio) == len(sub_lengths)
        for i, item in enumerate(sub_lengths):
            if not self.mem_save_mode:
                sub_indices = list(range(accumulate_length, accumulate_length + item))
            else:
                sub_indices = CustomizedRange(accumulate_length, accumulate_length + item)
            sub_indices = self._get_indices_with_ratio(sub_indices, ratio[i])
            indices_list += sub_indices
            accumulate_length += item

        if self.shuffle:
            random.shuffle(indices_list)
        if return_sub_indices:
            return indices_list
        indices = []
        for item in indices_list:
            indices += item
        return indices

    def create_chunk_indices_from_bz_and_worker(self, indices):
        # calculate num batches per worker
        num_batches = (self.num_samples + self.batch_size - 1) // self.batch_size
        last_batch_size = self.num_samples - (num_batches - 1) * self.batch_size
        num_batches_per_worker = num_batches // self.num_workers
        remain = num_batches - self.num_workers * num_batches_per_worker
        num_batches_per_each_worker = [num_batches_per_worker + 1] * remain + [num_batches_per_worker] * (self.num_workers - remain)
        assert sum(num_batches_per_each_worker) == num_batches
        last_batch_worker_id = self.num_workers - 1 if remain == 0 else remain - 1

        num_samples_per_worker = []
        for i in range(self.num_workers):
            if i == last_batch_worker_id:
                current_num_samples = (num_batches_per_each_worker[i] - 1) * self.batch_size + last_batch_size
            else:
                current_num_samples = num_batches_per_each_worker[i] * self.batch_size
            num_samples_per_worker.append(current_num_samples)
        assert sum(num_samples_per_worker) == self.num_samples
        start_idx_per_worker = [0] * self.num_workers
        for i in range(1, self.num_workers):
            start_idx_per_worker[i] = start_idx_per_worker[i - 1] + num_samples_per_worker[i - 1]

        if self.repeat and self.shuffle:
            random.seed(self.seed)
        while True:
            self.inner_epoch_count += 1
            current_idx_per_worker = [i for i in start_idx_per_worker]
            for i in range(num_batches):
                wid = i % self.num_workers
                start_idx = current_idx_per_worker[wid]
                end_idx = start_idx + self.batch_size
                is_last_batch = (end_idx - start_idx_per_worker[wid]) >= num_samples_per_worker[wid] and not self.repeat
                end_idx = min(end_idx, start_idx_per_worker[wid] + num_samples_per_worker[wid])
                if self.mem_save_mode:
                    yield indices.get_value_from(start_idx, end_idx, self.shuffle), is_last_batch
                else:
                    yield indices[start_idx: end_idx], is_last_batch
                current_idx_per_worker[wid] = end_idx

            if not self.repeat:
                break
            if self.global_shuffle:
                assert self.mem_save_mode is False
                random.shuffle(indices)
            elif self.shuffle:
                if self.mem_save_mode:
                    shift_offset = random.randint(0, len(indices.list_of_ranges))
                    indices.random_reset(shift_offset)
                else:
                    shift_offset = random.randint(0, len(indices))
                    indices = indices[shift_offset:] + indices[:shift_offset]
    
    def __iter__(self):
        indices = []
        if self.epoch == self.last_iter_epoch:
            indices = self.indices
        else:
            self.last_iter_epoch = self.epoch
            if isinstance(self.sub_lengths[0], list):
                sub_indices_list = []
                accumulate_length = 0
                for i, item in enumerate(self.sub_lengths):
                    sub_indices = self._get_indices(item, accumulate_length, True, [self.ratios[i]])
                    accumulate_length += sum(item)
                    sub_indices_list += sub_indices
                if self.shuffle:
                    random.shuffle(sub_indices_list)
                if not self.mem_save_mode:
                    for item in sub_indices_list:
                        indices += item
                else:
                    indices = RangesHolder(sub_indices_list)
            else:
                indices = self._get_indices(self.sub_lengths, ratio=self.ratios)
                if self.global_shuffle:
                    random.shuffle(indices)
            
            if not self.drop_last:
                # add extra samples to make it evenly divisible
                padding_size = self.total_size - len(indices)
                if padding_size <= len(indices):
                    if self.mem_save_mode:
                        indices.combine(indices.slice(0, padding_size))
                    else:
                        indices += indices[:padding_size]
                else:
                    assert self.mem_save_mode is False, "mem_save_mode is True, but padding_size is greater than indices length, which is not supported now"
                    indices += (indices * math.ceil(padding_size / len(indices)))[
                        :padding_size
                    ]
            else:
                # remove tail of data to make it evenly divisible.
                if self.mem_save_mode:
                    indices = indices.slice(0, self.total_size)
                else:
                    indices = indices[: self.total_size]
            assert len(indices) == self.total_size

            # we do the chunk sharding here
            if self.mem_save_mode:
                indices = indices.slice(self.rank * self.num_samples, self.num_samples)
                # indices = indices.to_list(self.shuffle)
            else:
                indices = indices[self.rank * self.num_samples : (self.rank + 1) * self.num_samples]
            self.indices = indices
        assert len(indices) == self.num_samples
        # further split the per rank indices into num_workers splits
        indices_generator = self.create_chunk_indices_from_bz_and_worker(indices)

        # skip the indices that already been consumed
        for i in range(self.resume_step):
            _ = next(indices_generator)

        # yield empty indices to let workers follow the original order
        # otherwise, the first generated indices would be consumed by worker 0
        # while they should be consumed by cur_wid
        cur_wid = self.resume_step % self.num_workers
        for i in range(cur_wid):
            yield [], False

        while True:
            try:
                self.step += 1
                yield next(indices_generator)
            except StopIteration:
                break

    def set_step(self, step):
        self.resume_step = step
        self.step = step
    
    def __len__(self):
        # this is a batch sampler, return the number of batches
        if not self.repeat:
            if self.drop_last:
                return self.num_samples // self.batch_size
            else:
                return (self.num_samples + self.batch_size - 1) // self.batch_size
        else:
            return 1000000000000

    def _set_ckpt(self, state):
        self.__dict__.update(state)

    def _get_ckpt(self):
        indices = self.__dict__.pop('indices', None)
        ckpt_state = copy.deepcopy(self.__dict__)
        ckpt_state['resume_step'] = self.step
        ckpt_state['last_iter_epoch'] = -1
        self.__dict__['indices'] = indices
        return ckpt_state


class AncMultiSourceSampler():
    def __init__(
        self,
        dataset,
        ratios,
        batch_size,
        world = 1,
        rank = 0,
        num_workers = 1,
        shuffle = False,
        drop_last = False,
        seed = 0,
        resume_step = 0,
        repeat = False,
        global_shuffle = False,
        chunk_granularity = -1,
        mem_save_mode = False,
    ):
        self.ratios = ratios
        self.seed = seed + rank
        assert repeat is True
        assert 0.9999 <= sum(ratios) <= 1.0001
        self.samplers = [AncSampler(
            dataset.get_sub_lengths(i),
            batch_size,
            world=world,
            rank=rank,
            num_workers=num_workers,
            shuffle=shuffle,
            drop_last=drop_last,
            seed=seed,
            resume_step=resume_step,
            repeat=repeat,
            global_shuffle=global_shuffle,
            chunk_granularity=chunk_granularity,
            mem_save_mode=mem_save_mode,
        ) for i in range(len(dataset))]
        self.random = random.Random(self.seed)
        self.shuffle = shuffle

    def __iter__(self):
        iters = [iter(sampler) for sampler in self.samplers]
        iter_list = list(range(len(iters)))
        if not self.shuffle:
            # if shuffle is False, we want every epoch sampler output the same indices
            self.random = random.Random(self.seed)
        while True:
            cur_iter_idx = self.random.choices(iter_list, weights=self.ratios)[0]
            cur_iter = iters[cur_iter_idx]
            indices, is_last_batch = next(cur_iter)
            yield cur_iter_idx, indices, is_last_batch

    def __len__(self):
        return 1000000000000

    def _get_ckpt(self):
        state = {}
        samplers_state = [sampler._get_ckpt() for sampler in self.samplers]
        state['samplers'] = samplers_state
        state['random_state'] = self.random.getstate()
        return state

    def _set_ckpt(self, state):
        assert len(state['samplers']) == len(self.samplers)
        for i, sampler in enumerate(self.samplers):
            sampler._set_ckpt(state['samplers'][i])
        self.random.setstate(state['random_state'])