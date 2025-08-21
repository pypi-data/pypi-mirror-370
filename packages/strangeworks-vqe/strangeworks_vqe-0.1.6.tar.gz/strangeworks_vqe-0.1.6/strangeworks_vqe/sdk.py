from typing import Optional

import strangeworks
from strangeworks.core.errors.error import StrangeworksError

import strangeworks_vqe.serializer as serializer
import strangeworks_vqe.utils as utils


class StrangeworksVQE:
    """Strangeworks client object."""

    def __init__(self, resource_slug: Optional[str] = " ") -> None:
        if resource_slug != " " and resource_slug != "":
            self.rsc = strangeworks.resources(slug=resource_slug)[0]
        else:
            rsc_list = strangeworks.resources()
            for rr in range(len(rsc_list)):
                if rsc_list[rr].product.slug == "vqe":
                    self.rsc = rsc_list[rr]

        self.backend_list = " "

    def backends(self):
        """
        To-Do: Add cross check as to which backends the current user actually has
          access to.
                Currently, this just lists all backends that could work with the qaoa
                  service.
        """

        all_backends = strangeworks.backends(backend_type_slugs=["sw-vqe"])

        aws_backends = []
        aws_sim_backends = []
        ibmq_backends = []
        ibm_cloud_backends = []
        ibm_sim_backends = []

        for bb in range(len(all_backends)):
            try:
                arn_str = all_backends[bb].remote_backend_id[0:3]
                # print(arn_str)
                if arn_str == "arn" and all_backends[bb].remote_status != "retired":
                    if (
                        all_backends[bb].name == "SV1"
                        or all_backends[bb].name == "TN1"
                        or all_backends[bb].name == "dm1"
                    ):
                        backend_temp = {
                            "name": all_backends[bb].name,
                            "provider": "AWS_Simulator",
                            "remote_status": all_backends[bb].remote_status,
                            "arn": all_backends[bb].remote_backend_id,
                        }
                        aws_sim_backends.append(backend_temp)
                    else:
                        backend_temp = {
                            "name": all_backends[bb].name,
                            "provider": "AWS",
                            "remote_status": all_backends[bb].remote_status,
                            "arn": all_backends[bb].remote_backend_id,
                        }
                        aws_backends.append(backend_temp)
            except AttributeError:
                None

            try:
                ibm_str = all_backends[bb].name[0:3]
                id_str = all_backends[bb].remote_backend_id[0:3]
                if ibm_str == "ibm":
                    if id_str == "ibm":
                        prov = "IBM_Cloud"
                        backend_temp = {
                            "backend_name": all_backends[bb].name,
                            "provider": prov,
                            "remote_status": all_backends[bb].remote_status,
                        }
                        ibm_cloud_backends.append(backend_temp)
                    else:
                        if all_backends[bb].name == "ibmq_qasm_simulator":
                            prov = "IBM_Simulator"
                            backend_temp = {
                                "backend_name": all_backends[bb].name,
                                "provider": prov,
                                "remote_status": all_backends[bb].remote_status,
                            }
                            ibm_sim_backends.append(backend_temp)
                        else:
                            prov = "IBMQ"
                            backend_temp = {
                                "backend_name": all_backends[bb].name,
                                "provider": prov,
                                "remote_status": all_backends[bb].remote_status,
                            }
                            ibmq_backends.append(backend_temp)
                elif ibm_str == "sim":
                    prov = "IBM_Simulator"
                    backend_temp = {
                        "backend_name": all_backends[bb].name,
                        "provider": prov,
                        "remote_status": all_backends[bb].remote_status,
                    }
                    ibm_sim_backends.append(backend_temp)
            except AttributeError:
                None

        self.backend_list = {
            "AWS": aws_backends,
            "AWS_Sim": aws_sim_backends,
            "IBMQ": ibmq_backends,
            "IBM_Cloud": ibm_cloud_backends,
            "IBM_Sim": ibm_sim_backends,
        }

        return self.backend_list

    def run(self, backend, H, problem_params):
        if self.backend_list == " ":
            self.backends()

        aws = False
        ibm = False
        for nn in range(len(self.backend_list["AWS"])):
            if self.backend_list["AWS"][nn]["name"] == backend:
                aws = True
                backend_id = self.backend_list["AWS"][nn]["arn"]

        for nn in range(len(self.backend_list["IBMQ"])):
            if self.backend_list["IBMQ"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_quantum"
                backend_id = self.backend_list["IBMQ"][nn]["backend_name"]

        for nn in range(len(self.backend_list["IBM_Cloud"])):
            if self.backend_list["IBM_Cloud"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_cloud"
                backend_id = self.backend_list["IBM_Cloud"][nn]["backend_name"]

        for nn in range(len(self.backend_list["AWS_Sim"])):
            if self.backend_list["AWS_Sim"][nn]["name"] == backend:
                aws = True
                backend_id = self.backend_list["AWS_Sim"][nn]["arn"]

        for nn in range(len(self.backend_list["IBM_Sim"])):
            if self.backend_list["IBM_Sim"][nn]["backend_name"] == backend:
                ibm = True
                channel = "ibm_quantum"
                backend_id = self.backend_list["IBM_Sim"][nn]["backend_name"]

        if ibm is False and aws is False:
            Exception()

        string_list = H.primitive.paulis.to_labels()
        coeffs_list = H.primitive.coeffs.tolist()
        Ham = [string_list, coeffs_list]

        shotsin = problem_params["shotsin"]
        maxiter = problem_params["maxiter"]
        nqubits = problem_params["nqubits"]
        optimizer = problem_params.get("optimizer", None)
        ansatz = problem_params.get("ansatz", None)

        hyperparams = {
            "H": serializer.pickle_serializer(H, "json"),
            "Ham": serializer.pickle_serializer(Ham, "json"),
            "nqubits": str(nqubits),
            "maxiter": str(maxiter),
            "optimizer": optimizer,
            "shotsin": str(shotsin),
            "ansatz": ansatz,
        }

        if aws is True:
            input_params = {
                "provider": "aws",
                "dev_str": backend_id,
                "hyperparams": hyperparams,
            }
        elif ibm is True:
            input_params = {
                "provider": "ibm",
                "channel": channel,
                "backend": backend_id,
                "hyperparams": hyperparams,
            }

        input_json = serializer.pickle_serializer(input_params, "json")
        input_json = {"payload": input_json}

        sw_job = strangeworks.execute(self.rsc, input_json, "run_hybrid_job")

        return sw_job

    def update_status(self, sw_job):
        if type(sw_job) is dict:
            job_slug = sw_job.get("slug")
        else:
            job_slug = sw_job.slug

        status = strangeworks.execute(
            self.rsc, {"payload": {"job_slug": job_slug}}, "status"
        )

        return status

    def get_results(self, sw_job, calculate_exact_sol=False, display_results=False):
        if type(sw_job) is dict:
            job_slug = sw_job.get("slug")
        else:
            job_slug = sw_job.slug

        sw_job = strangeworks.jobs(slug=job_slug)[0]
        result_url = None
        for file in sw_job.files:
            if file.file_name == "result.json":
                result_url = file.url

        if result_url:
            result_file = strangeworks.download_job_files([result_url])[0]
        else:
            result = strangeworks.execute(
                self.rsc, {"payload": {"job_slug": job_slug}}, "result"
            )

            if result.strip().upper() == "COMPLETED":
                sw_job = strangeworks.jobs(slug=job_slug)[0]

                result_url = None
                for file in sw_job.files:
                    if file.file_name == "result.json":
                        result_url = file.url

                if result_url:
                    result_file = strangeworks.download_job_files([result_url])[0]
                else:
                    raise StrangeworksError(f"unable to open {result_url}")
            else:
                return result

        if calculate_exact_sol:
            inputs_url = strangeworks.execute(
                self.rsc, {"payload": {"job_slug": job_slug}}, "get_inputs_url"
            )
            inputs = strangeworks.download_job_files([inputs_url])[0]

            try:
                H = serializer.pickle_deserializer(inputs["H"], "json")
            except Exception:
                H = serializer.pickle_deserializer(inputs["hyperparams"]["H"], "json")

            try:
                En_exact = utils.get_exact_en(H, H.num_qubits)
            except Exception:
                En_exact = "!!problem too big for exact solution!!"
            result_file["En_exact"] = En_exact
        else:
            result_file["En_exact"] = None

        if display_results:
            En_exact = result_file["En_exact"]
            En_sol = result_file["en_sol"]

            print(f"The energy of the solution found by the algorithm is {En_sol}")
            print(f"The exact optimal energy is {En_exact}")

        return result_file

    def job_list(self, update_status=True):
        job_list = strangeworks.jobs()

        qaoa_job_list = []
        for jj in range(len(job_list)):
            if job_list[jj].resource.product.slug == "vqe":
                if job_list[jj].external_identifier[0:3] == "arn":
                    prov = "AWS"
                else:
                    prov = "IBM"

                if job_list[jj].status != "COMPLETED" and update_status is True:
                    try:
                        status = strangeworks.execute(
                            self.rsc,
                            {"payload": {"job_slug": job_list[jj].slug}},
                            "status",
                        )
                    except Exception:
                        status = job_list[jj].status
                else:
                    status = job_list[jj].status

                temp = {
                    "slug": job_list[jj].slug,
                    "Status": status,
                    "Provider": prov,
                    "resource_slug": job_list[jj].resource.slug,
                }
                qaoa_job_list.append(temp)

        return qaoa_job_list
