import pypsa
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def perturb_network(
    n: pypsa.Network, tech_name: str, pert_opts: dict, copy_ntwk=False
) -> pypsa.Network:
    """

    Args:
        n (pypsa.Network): the pypsa network object to perturb
        tech_name (str): technology to perturb
        pert_opts (dict): options for the perturbation
        copy_ntwk (bool): make a copy of the network object or not

    Returns:
        pypsa.Network: the perturbed network
    """
    if copy_ntwk:
        n_pert = n.copy()
    else:
        n_pert = n

    n_pert.optimize.fix_optimal_capacities()

    # Perturb the network for technoloy pTech in wildcards
    n.generators.loc[n.generators.carrier == tech_name, "p_nom"] *= pert_opts["factor"]

    # TODO same for links! @Adrian
    n.links.loc[n.links.carrier == tech_name, "p_nom"] = True
    return n_pert


def solve_pert_network(n: pypsa.Network, config: dict):
    """solve the perturbed network

    Args:
        n (pypsa.Network): _description_
        config (dict): _description_
    """

    # deal with the gurobi license activation, which requires a tunnel to the login nodes
    solver_config = config["solving"]["solver"]
    gurobi_license_config = config["solving"].get("gurobi_hpc_tunnel", None)
    logger.info(f"Solver config {solver_config} and license cfg {gurobi_license_config}")

    # TODO is this really needed?
    n = prepare_network(n, solve_opts, config=config)

    # solve the network
    n = solve_network(
        n,
        config=config,
        params=params,
        solving=params.solving,
        log_fn=log.solver,
    )

    return n


def calc_covariance(n_base, n_pert, tech) -> pd.Dataframe:
    """_summary_

    Args:
        n_base (_type_): _description_
        n_pert (_type_): _description_
        tech (_type_): _description_
    Returns:
        ...
    """


def export_pert_n(n, add_meta: dict, out_p: os.PathLike):
    """_summary_

    Args:
        n (_type_): _description_
        add_meta (dict): additional metdz
        out_p (os.PathLike): _description_
    """
    meta_ = n.meta
    meta_.update(add_meta)
    n.meta = meta_
    n.export_to_netcdf(out_p)


if __name__ == "__main__":
    # wildcards for years here
    n_base = load_network(snakemake.input.base_network)
    opts = snakemake.config["subset"]
    # this is a settingd
    perturbation_techs = snakemake.config["..."]["perturbations"]
    for p_tech in perturbation_techs:
        n_pert = perturb_network(n_base, p_tech)
        n_solved = solve_pert_network()
        covar = calc_covariance(n_base, n_pert, p_tech, opts)
        export_pert_n(n_solved)
