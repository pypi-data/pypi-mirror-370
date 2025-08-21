# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Date    : 2023/12/14 
# @Function:
import time

from gevent import monkey
monkey.patch_all()
import numpy as np
import gevent.ssl
import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException


"""
############## 【安装 triton client】 ##############
文档：https://github.com/triton-inference-server/client
参考：https://github.com/triton-inference-server/client/blob/main/src/python/examples/simple_http_async_infer_client.py
pip install tritonclient
pip install geventhttpclient
or
pip install tritonclient[all]
sudo apt update
sudo apt install libb64-dev
"""


class ClientHttp(object):
    def __init__(self, url="localhost:8080", concurrency=1, connection_timeout=60.0, network_timeout=60.0, verbose=False,
                 ssl=False, key_file: str = None, cert_file: str = None, ca_certs: str = None, insecure=False):
        """
        创建客户端
        :param url: Inference server URL. Default is localhost:8000.
        :param concurrency: 并发数量
        :param connection_timeout: 连接超时
        :param network_timeout: 网络超时
        :param verbose: Enable verbose output
        :param ssl: Enable encrypted link to the server using HTTPS
        :param key_file: File holding client private key. Default is None.
        :param cert_file: File holding client certificate. Default is None.
        :param ca_certs: File holding ca certificate. Default is None.
        :param insecure: Use no peer verification in SSL communications. Use with caution. Default is False.
        :return:
        """
        self.url = url
        self.concurrency = concurrency
        self.connection_timeout = connection_timeout
        self.network_timeout = network_timeout
        self.verbose = verbose
        self.ssl = ssl
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_certs = ca_certs
        self.insecure = insecure
        self.client = self._create()

    def _create(self):
        try:
            if self.ssl:
                ssl_options = {}
                if self.key_file is not None:
                    ssl_options["keyfile"] = self.key_file
                if self.cert_file is not None:
                    ssl_options["certfile"] = self.cert_file
                if self.ca_certs is not None:
                    ssl_options["ca_certs"] = self.ca_certs
                ssl_context_factory = None
                if self.insecure:
                    ssl_context_factory = gevent.ssl._create_unverified_context
                return httpclient.InferenceServerClient(
                    url=self.url,
                    concurrency=self.concurrency,
                    connection_timeout=self.connection_timeout,
                    network_timeout=self.network_timeout,
                    verbose=self.verbose,
                    ssl=True,
                    ssl_options=ssl_options,
                    insecure=self.insecure,
                    ssl_context_factory=ssl_context_factory,
                )
            else:
                return httpclient.InferenceServerClient(
                    url=self.url, verbose=self.verbose
                )
        except Exception as e:
            raise Exception("channel creation failed: " + str(e))

    @staticmethod
    def build_input(name: str, data: np.asarray, datatype: str = "INT32", binary_data=False):
        """
        创建input
        :param name: The name of input whose data will be described by this object
        :param data: numpy array, The tensor data in numpy array format
        :param datatype: np.dtype: INT8|INT16|INT32|INT64|UINT8|UINT16|UINT32|UINT64|FP16|FP32|FP64
        :param binary_data:
        :return:
        """
        infer_input = httpclient.InferInput(name, data.shape, datatype)
        infer_input.set_data_from_numpy(data, binary_data=binary_data)
        return infer_input

    @staticmethod
    def build_output(name: str, binary_data=False):
        """
        创建output
        :param name: The name of output
        :param binary_data:
        :return:
        """
        return httpclient.InferRequestedOutput(name, binary_data=binary_data)

    def infer_sync(self, inputs: list, model_name: str, model_version: str = "", http_headers: dict = None,
                   request_compression_algorithm: str = None, response_compression_algorithm: str = None, outputs: list = None):
        """
        同步推理
        :param inputs: A list of InferInput objects, each describing data for a input tensor required by the model.
        :param outputs: A list of InferRequestedOutput objects, each describing how the output data must be returned.
               If not specified all outputs produced by the model will be returned using default settings.
        :param model_name: The name of the model to run inference.
        :param model_version: The version of the model to run inference.
        :param model_version:
        :param http_headers:
        :param request_compression_algorithm:  Optional HTTP compression algorithm to use for the request body on client side.
               Currently supports "deflate", "gzip" and None. By default, no compression is used.
        :param response_compression_algorithm: Optional HTTP compression algorithm to request for the response body.
               Note that the response may not be compressed if the server does not
               support the specified algorithm. Currently supports "deflate",
               "gzip" and None. By default, no compression is requested.
        :return:
        """
        try:
            results = self.client.infer(
                model_name=model_name,
                model_version=model_version,
                inputs=inputs,
                outputs=outputs,
                headers=http_headers,
                request_compression_algorithm=request_compression_algorithm,
                response_compression_algorithm=response_compression_algorithm,
            )
            return results
        except InferenceServerException as e:
            print(e)

    def infer_async(self, inputs: list, model_name: str, model_version: str = "", http_headers: dict = None, request_compression_algorithm: str = None, response_compression_algorithm: str = None, outputs: list = None):
        return self.client.async_infer(
            model_name=model_name,
            model_version=model_version,
            inputs=inputs,
            outputs=outputs,
            headers=http_headers,
            request_compression_algorithm=request_compression_algorithm,
            response_compression_algorithm=response_compression_algorithm,
        )

    def infer_sync_demo(self, data, infer_count=20):
        """
        同步推理demo
        :param data:
        :param infer_count:
        :return:
        """
        start = time.time()
        for i in range(0, infer_count):
            start_time = time.perf_counter()
            result = self.infer_sync(model_name="cosnet_onnx", model_version="1",
                                     inputs=[client.build_input(name="input_ids", data=data[0], datatype="INT64"),
                                             client.build_input(name="token_type_ids", data=data[1], datatype="INT64"),
                                             client.build_input(name="attention_mask", data=data[2], datatype="INT64")],
                                     outputs=[client.build_output(name="output", binary_data=True)])
            end_time = time.perf_counter()
            run_time = end_time - start_time
            print(f"单次预测的时间：{run_time}秒")
        print("平均推理耗时：{0:.5f}".format((time.time()-start)/infer_count))
        # start = time.time()
        # for i in range(0, infer_count):
        #     start_time = time.perf_counter()
        #     result = self.infer_sync(model_name="cosnet_onnx", model_version="1",
        #                              inputs=[client.build_input(name="input_ids", data=data[0], datatype="INT64"),
        #                                      client.build_input(name="token_type_ids", data=data[1], datatype="INT64"),
        #                                      client.build_input(name="attention_mask", data=data[2], datatype="INT64")],
        #                              outputs=[client.build_output(name="output", binary_data=True)])
        #     end_time = time.perf_counter()
        #     run_time = end_time - start_time
        #     print(f"单次预测的时间：{run_time}秒")
        # print("平均推理耗时：{0:.5f}".format((time.time()-start)/infer_count))

    def infer_async_demo(self, data, infer_count=20):
        """
        异步推理demo
        :param data:
        :param infer_count:
        :return:
        """
        async_requests = []
        start = time.time()
        for i in range(infer_count):
            async_requests.append(
                self.infer_async(model_name="cosnet_onnx", model_version="1",
                                 inputs=[client.build_input(name="input_ids", data=data[0], datatype="INT64"),
                                         client.build_input(name="token_type_ids", data=data[1], datatype="INT64"),
                                         client.build_input(name="attention_mask", data=data[2], datatype="INT64")],
                                 outputs=[client.build_output(name="output", binary_data=True)])
            )
        res_output = []
        for async_request in async_requests:
            start_time = time.perf_counter()
            # Get the result from the initiated asynchronous inference request.
            # Note the call will block till the server responds.
            res_output.append(async_request.get_result())
            end_time = time.perf_counter()
            run_time = end_time - start_time
            print(f"单次预测的时间：{run_time}秒")
        print("平均推理耗时：{0:.20f}".format((time.time()-start)/infer_count))
        # start = time.time()
        # async_requests = []
        # for i in range(infer_count):
        #     async_requests.append(
        #         self.infer_async(model_name="cosnet_tensorrt", model_version="1",
        #                          inputs=[client.build_input(name="input_ids", data=data[0], datatype="INT32"),
        #                                  client.build_input(name="token_type_ids", data=data[1], datatype="INT32"),
        #                                  client.build_input(name="attention_mask", data=data[2], datatype="INT32")],
        #                          outputs=[client.build_output(name="output", binary_data=True)])
        #     )
        # res_output = []
        # for async_request in async_requests:
        #     start_time = time.perf_counter()
        #     # Get the result from the initiated asynchronous inference request.
        #     # Note the call will block till the server responds.
        #     res_output.append(async_request.get_result())
        #     end_time = time.perf_counter()
        #     run_time = end_time - start_time
        #     print(f"单次预测的时间：{run_time}秒")
        # print("平均推理耗时：{0:.20f}".format((time.time()-start)/infer_count))


if __name__ == "__main__":
    from zhousflib.infer_framework.ann import to_numpy
    from zhousflib.infer_framework.ann.torch.torch_to_onnx import example_inputs_demo
    args = example_inputs_demo(input_size=1)
    data_arr = np.asarray([to_numpy(args[0].int()), to_numpy(args[1].int()), to_numpy(args[2].int())], dtype=np.int64)
    client = ClientHttp(url="127.0.0.1:5005", concurrency=100)
    """
    同步请求demo
    """
    client.infer_sync_demo(data=data_arr, infer_count=500)
    """
    异步请求demo
    """
    # client.infer_async_demo(data=data_arr, infer_count=10)
    pass
