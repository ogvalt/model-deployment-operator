from urllib.parse import quote, quote_plus
import json

from geventhttpclient import HTTPClient
from geventhttpclient.url import URL


def raise_error(msg):
    """
    Raise error with the provided message
    """
    raise Exception(msg=msg) from None

def _get_query_string(query_params):
    params = []
    for key, value in query_params.items():
        if isinstance(value, list):
            for item in value:
                params.append("%s=%s" % (quote_plus(key), quote_plus(str(item))))
        else:
            params.append("%s=%s" % (quote_plus(key), quote_plus(str(value))))
    if params:
        return "&".join(params)
    return ""



def _raise_if_error(response):
    """
    Raise :py:class:`InferenceServerException` if received non-Success
    response from the server
    """
    error = _get_error(response)
    if error is not None:
        raise error
    
def _get_error(response):
    """
    Returns the :py:class:`InferenceServerException` object if response
    indicates the error. If no error then return None
    """
    if response.status_code != 200:
        body = None
        try:
            body = response.read().decode("utf-8")
            error_response = (
                json.loads(body)
                if len(body)
                else {"error": "client received an empty response from the server."}
            )
            return Exception(
                msg=error_response["error"], status=str(response.status_code)
            )
        except Exception as e:
            return Exception(
                msg=f"an exception occurred in the client while decoding the response: {e}",
                status=str(response.status_code),
                debug_details=body,
            )
    else:
        return None
    
class Request:
    """A request object.

    Parameters
    ----------
    headers : dict
        A dictionary containing the request headers.
    """

    def __init__(self, headers):
        self.headers = headers if headers is not None else {}


class InferenceServerClient:
    """An InferenceServerClient object is used to perform any kind of
    communication with the InferenceServer using http protocol. None
    of the methods are thread safe. The object is intended to be used
    by a single thread and simultaneously calling different methods
    with different threads is not supported and will cause undefined
    behavior.

    Parameters
    ----------
    url : str
        The inference server name, port and optional base path
        in the following format: host:port/<base-path>, e.g.
        'localhost:8000'.

    verbose : bool
        If True generate verbose output. Default value is False.
    concurrency : int
        The number of connections to create for this client.
        Default value is 1.
    connection_timeout : float
        The timeout value for the connection. Default value
        is 60.0 sec.
    network_timeout : float
        The timeout value for the network. Default value is
        60.0 sec
    max_greenlets : int
        Determines the maximum allowed number of worker greenlets
        for handling asynchronous inference requests. Default value
        is None, which means there will be no restriction on the
        number of greenlets created.
    ssl : bool
        If True, channels the requests to encrypted https scheme.
        Some improper settings may cause connection to prematurely
        terminate with an unsuccessful handshake. See
        `ssl_context_factory` option for using secure default
        settings. Default value for this option is False.
    ssl_options : dict
        Any options supported by `ssl.wrap_socket` specified as
        dictionary. The argument is ignored if 'ssl' is specified
        False.
    ssl_context_factory : SSLContext callable
        It must be a callbable that returns a SSLContext. Set to
        `gevent.ssl.create_default_context` to use contexts with
        secure default settings. This should most likely resolve
        connection issues in a secure way. The default value for
        this option is None which directly wraps the socket with
        the options provided via `ssl_options`. The argument is
        ignored if 'ssl' is specified False.
    insecure : bool
        If True, then does not match the host name with the certificate.
        Default value is False. The argument is ignored if 'ssl' is
        specified False.

    Raises
    ------
    Exception
        If unable to create a client.

    """

    def __init__(
        self,
        url,
        verbose=False,
        concurrency=1,
        connection_timeout=60.0,
        network_timeout=60.0,
        ssl=False,
        ssl_options=None,
        ssl_context_factory=None,
        insecure=False,
    ):
        super().__init__()
        if url.startswith("http://") or url.startswith("https://"):
            raise_error("url should not include the scheme")
        scheme = "https://" if ssl else "http://"
        self._parsed_url = URL(scheme + url)
        self._base_uri = self._parsed_url.request_uri.rstrip("/")
        self._client_stub = HTTPClient.from_url(
            self._parsed_url,
            concurrency=concurrency,
            connection_timeout=connection_timeout,
            network_timeout=network_timeout,
            ssl_options=ssl_options,
            ssl_context_factory=ssl_context_factory,
            insecure=insecure,
        )
        self._verbose = verbose
        

    def _validate_headers(self, headers):
        """Checks for any unsupported HTTP headers before processing a request.

        Parameters
        ----------
        headers: dict
            HTTP headers to validate before processing the request.

        Raises
        ------
        InferenceServerException
            If an unsupported HTTP header is included in a request.
        """
        if not headers:
            return

        # HTTP headers are case-insensitive, so force lowercase for comparison
        headers_lowercase = {k.lower(): v for k, v in headers.items()}
        # The python client lirary (and geventhttpclient) do not encode request
        # data based on "Transfer-Encoding" header, so reject this header if
        # included. Other libraries may do this encoding under the hood.
        # The python client library does expose special arguments to support
        # some "Content-Encoding" headers.
        if "transfer-encoding" in headers_lowercase:
            raise_error(
                "Unsupported HTTP header: 'Transfer-Encoding' is not "
                "supported in the Python client library. Use raw HTTP "
                "request libraries or the C++ client instead for this "
                "header."
            )  

    def _get(self, request_uri, headers, query_params):
        """Issues the GET request to the server

        Parameters
        ----------
        request_uri: str
            The request URI to be used in GET request.
        headers: dict
            Additional HTTP headers to include in the request.
        query_params: dict
            Optional url query parameters to use in network
            transaction.

        Returns
        -------
        geventhttpclient.response.HTTPSocketPoolResponse
            The response from server.

        """
        request = Request(headers)

        # Update the headers based on plugin invocation
        headers = request.headers
        self._validate_headers(headers)

        if self._base_uri is not None:
            request_uri = self._base_uri + "/" + request_uri

        if query_params is not None:
            request_uri = request_uri + "?" + _get_query_string(query_params)

        if self._verbose:
            print("GET {}, headers {}".format(request_uri, headers))

        if headers is not None:
            response = self._client_stub.get(request_uri, headers=headers)
        else:
            response = self._client_stub.get(request_uri)

        if self._verbose:
            print(response)

        return response
    
    def _post(self, request_uri, request_body, headers, query_params):
        """Issues the POST request to the server

        Parameters
        ----------
        request_uri: str
            The request URI to be used in POST request.
        request_body: str
            The body of the request
        headers: dict
            Additional HTTP headers to include in the request.
        query_params: dict
            Optional url query parameters to use in network
            transaction.

        Returns
        -------
        geventhttpclient.response.HTTPSocketPoolResponse
            The response from server.
        """
        request = Request(headers)

        # Update the headers based on plugin invocation
        headers = request.headers
        self._validate_headers(headers)

        if self._base_uri is not None:
            request_uri = self._base_uri + "/" + request_uri

        if query_params is not None:
            request_uri = request_uri + "?" + _get_query_string(query_params)

        if self._verbose:
            print("POST {}, headers {}\n{}".format(request_uri, headers, request_body))

        if headers is not None:
            response = self._client_stub.post(
                request_uri=request_uri, body=request_body, headers=headers
            )
        else:
            response = self._client_stub.post(
                request_uri=request_uri, body=request_body
            )

        if self._verbose:
            print(response)

        return response

    def is_model_ready(
        self, model_name, model_version="", headers=None, query_params=None
    ):
        """Contact the inference server and get the readiness of specified model.

        Parameters
        ----------
        model_name: str
            The name of the model to check for readiness.
        model_version: str
            The version of the model to check for readiness. The default value
            is an empty string which means then the server will choose a version
            based on the model and internal policy.
        headers: dict
            Optional dictionary specifying additional HTTP
            headers to include in the request.
        query_params: dict
            Optional url query parameters to use in network
            transaction.

        Returns
        -------
        bool
            True if the model is ready, False if not ready.

        Raises
        ------
        Exception
            If unable to get model readiness.

        """
        if type(model_version) != str:
            raise_error("model version must be a string")
        if model_version != "":
            request_uri = "v2/models/{}/versions/{}/ready".format(
                quote(model_name), model_version
            )
        else:
            request_uri = "v2/models/{}/ready".format(quote(model_name))

        response = self._get(
            request_uri=request_uri, headers=headers, query_params=query_params
        )

        return response.status_code == 200
    
    def get_model_repository_index(self, headers=None, query_params=None):
        """Get the index of model repository contents

        Parameters
        ----------
        headers: dict
            Optional dictionary specifying additional
            HTTP headers to include in the request
        query_params: dict
            Optional url query parameters to use in network
            transaction

        Returns
        -------
        dict
            The JSON dict holding the model repository index.

        Raises
        ------
        InferenceServerException
            If unable to get the repository index.

        """
        request_uri = "v2/repository/index"
        response = self._post(
            request_uri=request_uri,
            request_body="",
            headers=headers,
            query_params=query_params,
        )
        _raise_if_error(response)

        content = response.read()
        if self._verbose:
            print(content)

        return json.loads(content)

    