#!/bin/bash

#SBATCH --account=ml4science
#SBATCH --partition=a100_normal_q
#SBATCH --time=0-16:00:00 
#SBATCH --gres=gpu:1 
#SBATCH --nodes=1 --ntasks-per-node=1 --cpus-per-task=8
#SBATCH -o ./SLURM/slurm-%j.out

module reset

module load Anaconda3/2020.11
module load gcc/8.2.0

source activate taming3 

#python -m 
wandb agent mndhamod/Phylo-VQVAE/q58r7rik
# wandb agent mndhamod/Phylo-VQVAE/kih79ivc
# wandb agent mndhamod/Phylo-VQVAE/wmpsdu5l

# To create a sweep:
# wandb sweep --project Phylo-VQVAE hyperp/hyperp_bayes_nested.yaml 
# wandb sweep --project Phylo-VQVAE hyperp/hyperp_bayes_phyloloss_nested.yaml
# wandb sweep --project Phylo-VQVAE hyperp/hyperp_grid_phyloloss_codebookperlevel_nested.yaml
# wandb sweep --project Phylo-VQVAE hyperp/hyperp_grid_phyloloss_numcodebooks_nested.yaml
# wandb sweep --project Phylo-VQVAE hyperp/hyperp_grid_phyloloss_numphylochannels_nested.yaml

exit;