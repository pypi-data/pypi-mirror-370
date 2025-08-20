from anc.api.connection import Connection
from requests.exceptions import RequestException
import os
import sys
import json
from rich.console import Console
from rich.table import Table, box
from rich.text import Text

MM_BASE_URL = "http://model-management-service.infra.svc.cluster.local:5000"


def trigger_eval_job(
    run_id: str,
    model_name: str,
    project_name: str,
    ckpt_list: list[str],
    dataset_list: list[str],
    tp: int,
    pp: int,
    ep: int,
    seq_len: int,
    batch_size: int,
    tokenizer_path: str,
    validation_batch_size: int,
    dataset_tasks: str = None,
    model_args: str = None,
    wandb_project: str = None,
    wandb_api_key: str = None,
) -> bool:
    cluster = os.environ.get("MLP_CLUSTER", "il2")
    project = os.environ.get("MLP_PROJECT", "llm")
    
    data = {
        "evaluation_id": run_id,
        "modality": "nlp",
        "model_name": model_name,
        "project_name": project_name,
        "eval_ckpt_list": ckpt_list,
        "eval_dataset_list": dataset_list,
        "project": project,
        "cluster": cluster,
        "eval_tp": tp,
        "eval_pp": pp,
        "eval_ep": ep,
        "eval_seqlen": seq_len,
        "eval_batch_size": batch_size,
        "eval_tokenizer_path": tokenizer_path,
        "status": "start",
        "validation_batch_size": validation_batch_size,
    }
    
    # Add dataset_tasks to data if provided
    if dataset_tasks:
        data["eval_tasks"] = dataset_tasks
    
    if model_args:
        data["model_args"] = model_args
    
    if wandb_project and wandb_api_key:
        data["wandb_project"] = wandb_project
        data["wandb_api_key"] = wandb_api_key

    try:
        conn = Connection(url=MM_BASE_URL)
        response = conn.post("/evaluations", json=data)

        # Check if the status code is in the 2xx range
        if 200 <= response.status_code < 300:
            response_data = response.json()
            evaluation_id = response_data.get('evaluation_id')
            if evaluation_id:
                print(f"Evaluation task added successfully. Your Eval ID is: \033[92m{evaluation_id}\033[0m")
                print(f"You can check the status of your evaluation using: \033[96manc eval status {evaluation_id}\033[0m")
                print(f"All historical results can be viewed at: \033[94mhttp://model.anuttacon.ai/models/467e151d-a52a-47f9-8791-db9c776635db/evaluations\033[0m")
            else:
                print("Evaluation failed, didn't get the evaluation id")
        else:
            #print(f"Error: Server responded with status code {response.status_code}")
            print(f"{response.text}")

    except RequestException as e:
        print(f"Sorry, you can't add dataset out of clusters, please use it in a notebook")
    except json.JSONDecodeError:
        print("Sorry: received invalid JSON response from server")
    except KeyboardInterrupt:
        print(f"Operation interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"Sorry, your command run failed, you can try again or reach out infra team")


def display_evaluation_status(evaluation_id: str):
    conn = Connection(url=MM_BASE_URL)
    response = conn.get(f"/evaluations/{evaluation_id}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Create a Rich console instance
        console = Console(width=200)  # Set wider console width
        
        # Display basic evaluation information
        eval_info = Table(title=f"Evaluation ID: {evaluation_id}", box=box.ROUNDED)
        eval_info.add_column("Parameter", style="cyan")
        eval_info.add_column("Value", style="green")
        
        # Add some key evaluation parameters
        eval_info.add_row("Model Name", data.get('model_name') or 'N/A')
        eval_info.add_row("Project", data.get('project') or 'N/A')
        eval_info.add_row("Submitted At", data.get('submitted_at') or 'N/A')
        
        console.print(eval_info)
        console.print()
        
        # Parse and display the evaluation_results_info
        if data.get('evaluation_results_info'):
            try:
                results_info = json.loads(data['evaluation_results_info'])
                
                # Create table for evaluation results with expanded width
                results_table = Table(title="Evaluation Results", box=box.ROUNDED, show_lines=True)
                results_table.add_column("Checkpoint", style="magenta", width=50, no_wrap=True)
                results_table.add_column("Dataset", style="blue", width=25, no_wrap=True)
                results_table.add_column("Endpoint URL", style="yellow", no_wrap=True)
                
                # Add rows for each checkpoint and dataset combination
                for ckpt_path, dataset_list in results_info.items():
                    # Get basename for the checkpoint
                    ckpt_basename = os.path.basename(ckpt_path)
                    
                    # Handle the case where each checkpoint has multiple datasets
                    for dataset_info in dataset_list:
                        if len(dataset_info) >= 4:
                            # Extract dataset info
                            dataset_path = dataset_info[0]
                            endpoint_url = dataset_info[1]
                            job_id = dataset_info[2]
                            status = dataset_info[3]
                            
                            # Get basename for dataset
                            dataset_basename = os.path.basename(dataset_path)
                            
                            results_table.add_row(
                                ckpt_basename,
                                dataset_basename,
                                endpoint_url
                            )
                
                # Ensure the table doesn't truncate content
                console.print(results_table)
            except json.JSONDecodeError:
                console.print(f"[red]Error parsing evaluation results info: {data['evaluation_results_info']}[/red]")
        else:
            console.print("[yellow]No evaluation results information available.[/yellow]")
    else:
        console.print(f"[red]Error retrieving evaluation status: {response.text}[/red]")
    