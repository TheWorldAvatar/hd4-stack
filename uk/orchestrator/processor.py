import requests
import time
import logging

from storeclient import RemoteStoreClient
import sparql_builder as qb
from common_namespaces import RDF_TYPE, DCTERMS_TITLE


logger = logging.getLogger(__name__)

STACK_HOST = "http://localhost:3838"

FTA_PREPROCESS_TRAJECTORY_ROUTE = "preprocess"
FTA_INSTANTIATE_TRAJECTORY_ROUTE = "instantiate"
PROCESS_TRAJECTORY_ROUTE = "process_trajectory"
CALCULATE_EXPOSURE_ROUTE = "calculate_exposure"
EXPORT_CSV_TRAJ_ROUTE = "csv_export/trajectory"
GENERATE_LAYER_ROUTE = ""

TIMEOUT = 3600

TWA_BASE_URL = "https://www.theworldavatar.com/kg/"

# DCAT
DCAT_BASE_URL = "http://www.w3.org/ns/dcat#"
DCAT_DATASET = DCAT_BASE_URL + "Dataset"
# OntoDevice
OD_BASE_URL = "https://www.theworldavatar.com/kg/ontodevice.owl/"
OD_POINT = OD_BASE_URL + "Point"
# OntoTimeSeries
OTS_BASE_URL = "https://www.theworldavatar.com/kg/ontotimeseries/"
OTS_HAS_TIMESERIES = OTS_BASE_URL + "hasTimeSeries"
# OntoExposure
OE_BASE_URL = "https://www.theworldavatar.com/kg/ontoexposure/"
OE_TRAJECTORY_COUNT = OE_BASE_URL + "TrajectoryCount"
OE_TRAJECTORY_AREA = OE_BASE_URL + "TrajectoryArea"
OE_TRAJECTORY_AREA_WGT_SUM = OE_BASE_URL + "TrajectoryAreaWeightedSum"
#https://www.theworldavatar.com/kg/ontoexposure/Count
#https://www.theworldavatar.com/kg/ontoexposure/Area
#https://www.theworldavatar.com/kg/ontoexposure/AreaWeightedSum
OE_HAS_DISTANCE = OE_BASE_URL + "hasDistance"


def log_msg(msg: str, level = logging.INFO) -> None:
    """
    Utility function that prints a message to the console and
    appends the same message to a log file for record keeping.
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    logger.log(level, f"{timestamp}: {msg}")
    if level >= logger.getEffectiveLevel():
        print(f"{timestamp}: WARNING: {msg}" if level == logging.WARN
            else f"{timestamp}: {msg}")


class TripleStore:

    def __init__(self, query_url: str) -> None:
        self.query_url = query_url
        self.store_client = RemoteStoreClient(query_url)


class TrajectoryStore(TripleStore):

    def get_trajectory_iris(self) -> list[str]:
        """
        Queries the triple store for OntoDevice:Point instances
        that have a timeseries and returns the list of Point IRIs.
        """
        sb = qb.SPARQLSelectBuilder()
        pointVarName = "point"
        tsVarName = "ts"
        sb.addVar(qb.makeVarRef(pointVarName))
        sb.addWhere(qb.makeVarRef(pointVarName),
            qb.makeIRIRef(OTS_HAS_TIMESERIES), qb.makeVarRef(tsVarName))
        sb.addWhere(qb.makeVarRef(pointVarName),
            qb.makeIRIRef(RDF_TYPE), qb.makeIRIRef(OD_POINT))
        query_str = sb.build()
        response = self.store_client.query(query_str)
        return [b[pointVarName]["value"] for b in response["results"]["bindings"]]


class EnvironmentalDataStore(TripleStore):

    def get_dataset_iris(self) -> dict[str, str]:
        """
        Queries the triple store for environmental datasets and returns a
        dictionary with the dataset titles as keys and their IRIs as values.
        """
        sb = qb.SPARQLSelectBuilder()
        datasetVarName = "dataset"
        titleVarName = "title"
        sb.addVar(qb.makeVarRef(datasetVarName))
        sb.addVar(qb.makeVarRef(titleVarName))
        sb.addWhere(qb.makeVarRef(datasetVarName),
            qb.makeIRIRef(RDF_TYPE), qb.makeIRIRef(DCAT_DATASET))
        sb.addWhere(qb.makeVarRef(datasetVarName),
            qb.makeIRIRef(DCTERMS_TITLE), qb.makeVarRef(titleVarName))
        query_str = sb.build()
        response = self.store_client.query(query_str)
        return {b[titleVarName]["value"]:b[datasetVarName]["value"] for b in response["results"]["bindings"]}


class MetricStore(TripleStore):

    def _instantiate_metric(self, type_iri: str, distance: int) -> str:
        """
        Instantiates an exposure metric by adding hard-coded triples
        to the triple store.
        """
        ub = qb.SPARQLUpdateBuilder()
        metric_iri = f"{TWA_BASE_URL}{type_iri.rstrip(' /').split('/')[-1]}{str(distance)}m"
        ub.addInsert(
            qb.makeIRIRef(metric_iri), "a", qb.makeIRIRef(type_iri)
        )
        ub.addInsert(
            qb.makeIRIRef(metric_iri),
            qb.makeIRIRef(OE_HAS_DISTANCE),
            f'"{str(distance)}"'
        )
        update_str = ub.build()
        self.store_client.update(update_str)
        return metric_iri

    def instantiate_metrics(self) -> None:
        """
        Instantiates some exposure metrics.
        """
        self._instantiate_metric(OE_TRAJECTORY_COUNT, 50)
        self._instantiate_metric(OE_TRAJECTORY_AREA, 50)

    def get_metric_iris(self, type_iri: str) -> list[str]:
        sb = qb.SPARQLSelectBuilder()
        metricVarName = "metric"
        sb.addVar(qb.makeVarRef(metricVarName))
        sb.addWhere(qb.makeVarRef(metricVarName),
            qb.makeIRIRef(RDF_TYPE), qb.makeIRIRef(type_iri))
        query_str = sb.build()
        response = self.store_client.query(query_str)
        return [b[metricVarName]["value"] for b in response["results"]["bindings"]]


class Agent:

    def __init__(self, base_url: str) -> None:
        self.base_url = f"{base_url.rstrip(' /')}/"


class TrajectoryAgent(Agent):

    def preprocess(self, timeout: int) -> str:
        """
        Runs trajectory preprocessing.
        """
        url = f"{self.base_url}{FTA_PREPROCESS_TRAJECTORY_ROUTE}"
        r = requests.post(url, params={}, timeout=timeout)
        r.raise_for_status()
        return r.text

    def instantiate(self, timeout: int) -> str:
        """
        Runs trajectory instantiation.
        """
        url = f"{self.base_url}{FTA_INSTANTIATE_TRAJECTORY_ROUTE}"
        r = requests.post(url, params={}, timeout=timeout)
        r.raise_for_status()
        return r.text


class TripAgent(Agent):

    def process_trajectory(self, iri: str, timeout: int) -> str:
        """
        Runs trip detection for a trajectory.
        """
        url = f"{self.base_url}{PROCESS_TRAJECTORY_ROUTE}"
        r = requests.post(url, params={"iri": iri}, timeout=timeout)
        r.raise_for_status()
        return r.text


class ExposureCalculationAgent(Agent):

    def calculate_exposure(self, subject: str, exposure: str, calculation: str, timeout: int) -> str:
        url = f"{self.base_url}{CALCULATE_EXPOSURE_ROUTE}"
        params = {
            "subject": subject,
            "exposure": exposure,
            "calculation": calculation
        }
        r = requests.post(url, json=params, timeout=timeout)
        r.raise_for_status()
        return r.text

    def export_csv(self, traj_iri: str,
        metric_type_iri: str | list[str],
        exposure_table: str | list[str],
        include_lat_lng: bool,
        refresh_of_cache: bool,
        timeout: int,
        filename: str
    ) -> str:
        url = f"{self.base_url}{EXPORT_CSV_TRAJ_ROUTE}"
        params = {
            "subject": traj_iri,
            "rdf_type": metric_type_iri,
            "exposure_table": exposure_table,
            "include_lat_lng": include_lat_lng,
            "refresh_of_cache": refresh_of_cache
        }
        r = requests.get(url, params=params, timeout=timeout)
        log_msg(f"Request URL: {r.request.url}")
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
        return f"Wrote file '{filename}'."


class TripLayerGenerator(Agent):

    def generate(self, iri: str, layer_group_name: str, host: str,
        layer_name: str, colour: str, width: int, timeout: int
    ) -> str:
        url = f"{self.base_url}{GENERATE_LAYER_ROUTE}"
        params = {
            "iri": iri,
            "layerGroupName": layer_group_name,
            "host": host,
            "layerName": layer_name,
            "colour": colour,
            "width": width
        }
        r = requests.post(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.text


def instantiate_trajectories():
    traj_agent = TrajectoryAgent(f"{STACK_HOST}/fenland-trajectory-agent")
    log_msg("Preprocessing trajectories...")
    log_msg(traj_agent.preprocess(TIMEOUT))
    log_msg("Instantiating trajectories...")
    log_msg(traj_agent.instantiate(TIMEOUT))


def instantiate():
    instantiate_trajectories()
    time.sleep(5)
    trajectory_store = TrajectoryStore(f"{STACK_HOST}/blazegraph/namespace/hd4/sparql")
    traj_iris = trajectory_store.get_trajectory_iris()
    #print(f"Trajectory IRIs: {traj_iris}")
    env_store = EnvironmentalDataStore(f"{STACK_HOST}/blazegraph/namespace/kb/sparql")
    env_dataset_iris = env_store.get_dataset_iris()
    log_msg(f"Environmental datasets:\n{str(env_dataset_iris)}")
    metric_store = MetricStore(f"{STACK_HOST}/blazegraph/namespace/hd4/sparql")
    metric_store.instantiate_metrics()
    count_metric_iris = metric_store.get_metric_iris(OE_TRAJECTORY_COUNT)
    area_metric_iris = metric_store.get_metric_iris(OE_TRAJECTORY_AREA)
    log_msg(f"Trajectory count metrics: {str(count_metric_iris)}")
    log_msg(f"Trajectory area metrics: {str(area_metric_iris)}")
    trip_agent = TripAgent(f"{STACK_HOST}/trip-agent")
    exp_calc_agent = ExposureCalculationAgent(f"{STACK_HOST}/exposure-calculation-agent")
    layer_generator = TripLayerGenerator(f"{STACK_HOST}/trip-layer-generator/")
    for traj_iri in traj_iris:
        log_msg(f"Detecting trips for trajectory '{traj_iri}'...")
        log_msg(trip_agent.process_trajectory(traj_iri, timeout=TIMEOUT))
        for exp_key in env_dataset_iris:
            log_msg(f"Calculating exposure of '{exp_key}' to trajectory '{traj_iri}'...")
            log_msg(exp_calc_agent.calculate_exposure(
                traj_iri, env_dataset_iris[exp_key], count_metric_iris[0], TIMEOUT))
        exp_key = "greenspace_sites"
        log_msg(f"Calculating exposure of '{exp_key}' to trajectory '{traj_iri}'...")
        log_msg(exp_calc_agent.calculate_exposure(
            traj_iri, env_dataset_iris[exp_key], area_metric_iris[0], TIMEOUT))
        time.sleep(1)
        log_msg(f"Generating GeoServer layers for trajectory '{traj_iri}'...")
        log_msg(layer_generator.generate(traj_iri, "Trajectories", STACK_HOST,
            f"trajectory_{traj_iri.rstrip(' /')[-8:]}", "cyan", 3, TIMEOUT))


def export_results():
    trajectory_store = TrajectoryStore(f"{STACK_HOST}/blazegraph/namespace/hd4/sparql")
    traj_iris = trajectory_store.get_trajectory_iris()
    env_store = EnvironmentalDataStore(f"{STACK_HOST}/blazegraph/namespace/kb/sparql")
    env_dataset_iris = env_store.get_dataset_iris()
    exp_calc_agent = ExposureCalculationAgent(f"{STACK_HOST}/exposure-calculation-agent")
    for traj_iri in traj_iris:
        log_msg(f"Exporting CSV for trajectory '{traj_iri}'...")
        log_msg(exp_calc_agent.export_csv(traj_iri,
            [OE_TRAJECTORY_COUNT, OE_TRAJECTORY_AREA],
            list(env_dataset_iris.keys()), True, True, TIMEOUT,
            f"trajectory_{traj_iri.rstrip(' /')[-8:]}.csv"))


def main():
    logging.basicConfig(filename="job.log",
        encoding="UTF-8", level=logging.INFO)
    instantiate()
    export_results()


if __name__== '__main__':
    main()
