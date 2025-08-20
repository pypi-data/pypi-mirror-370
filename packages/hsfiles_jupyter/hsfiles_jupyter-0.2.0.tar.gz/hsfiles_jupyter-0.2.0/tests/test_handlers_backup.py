import json
import os
from http.cookies import SimpleCookie
from typing import Union
import pytest

from jupyter_server.base.handlers import JupyterHandler

from asynctest import CoroutineMock, patch, PropertyMock
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import HTTPHeaders
from tornado.web import Application, RequestHandler
from tornado.testing import AsyncHTTPTestCase, gen_test
from hsclient import HydroShare
from hsfiles_jupyter.handlers import (
    UploadFileHandler as OriginalUploadFileHandler,
    RefreshFileHandler as OriginalRefreshFileHandler,
    DeleteFileHandler as OriginalDeleteFileHandler,
    CheckFileStatusHandler as OriginalCheckFileStatusHandler,
)
from hsfiles_jupyter.upload_file import upload_file_to_hydroshare
from hsfiles_jupyter.refresh_file import refresh_file_from_hydroshare
from hsfiles_jupyter.delete_file import delete_file_from_hydroshare
from hsfiles_jupyter.check_file_status import check_file_status
from hsfiles_jupyter.utils import get_credentials

# Set the ASYNC_TEST_TIMEOUT environment variable
os.environ["ASYNC_TEST_TIMEOUT"] = "60"  # Set timeout to 60 seconds

class BaseHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass

class UploadFileHandler(BaseHandler, OriginalUploadFileHandler):
    pass

class RefreshFileHandler(BaseHandler, OriginalRefreshFileHandler):
    pass

class DeleteFileHandler(BaseHandler, OriginalDeleteFileHandler):
    pass

class CheckFileStatusHandler(BaseHandler, OriginalCheckFileStatusHandler):
    pass

def get_user_cookie(headers: HTTPHeaders) -> Union[str, None]:
    cookies = headers.get("Set-Cookie", "")
    print(f">> Cookies: {cookies}")
    cookie = SimpleCookie()
    for cookie_str in cookies.split(';'):
        cookie.load(cookie_str.strip())
    # for cookie_str in cookies:
    # cookie.load(cookies)
    print(f">> Cookie: {cookie}")
    auth_cookie = None
    if "AUTH_SESSION_ID" in cookie:
        auth_cookie = cookie["AUTH_SESSION_ID"]
    elif "AUTH_SESSION_ID_LEGACY" in cookie:
        auth_cookie = cookie["AUTH_SESSION_ID_LEGACY"]
    if auth_cookie:
        return f"{auth_cookie.key}={auth_cookie.value};"
    return None

# @pytest.mark.usefixtures("resource_file_path")  # Ensures fixture setup
class TestHandlers(AsyncHTTPTestCase):
    def get_app(self):
        return Application([
            (r"/hydroshare/upload", UploadFileHandler),
            (r"/hydroshare/refresh", RefreshFileHandler),
            (r"/hydroshare/delete", DeleteFileHandler),
            (r"/hydroshare/status", CheckFileStatusHandler),
        ], cookie_secret="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6", xsrf_cookies=False)

    # @pytest.fixture(autouse=True)
    # def setup_fixtures(self, request):
    #     """Retrieve pytest fixtures before each test."""
    #     self.resource_file_path = request.getfixturevalue("resource_file_path")

    # def get_http_client(self):
    #     return AsyncHTTPClient(defaults=dict(request_timeout=30))  # Set timeout to 20 seconds

    async def set_auth_cookies(self):
        username, password = get_credentials()
        hs = HydroShare(username=username, password=password)
        hs_session = hs._hs_session
        response = hs_session.get("/home", status_code=200)
        self._auth_cookie = get_user_cookie(response.headers)

    # @gen_test
    # async def test_hydroshare_authenticate(self):
    #     username, password = get_credentials()
    #     hs = HydroShare(username=username, password=password)
    #     assert hs is not None

    async def run_test(self, url, mock_function, mock_return_value, mock_current_user, mock_prepare):
        mock_current_user.return_value = "test_user"
        mock_prepare.return_value = None
        mock_function.return_value = mock_return_value
        response = await self.http_client.fetch(
            self.get_url(url),
            method='POST',
            headers={"Content-Type": "application/json"},
            body=json.dumps({"path": "test_file_path"})
        )
        assert response.code == 200
        assert json.loads(response.body) == {"response": mock_return_value}

    # @pytest.mark.usefixtures("resource_file_path")
    @patch('jupyter_server.base.handlers.JupyterHandler.current_user', new_callable=PropertyMock)
    @patch('jupyter_server.base.handlers.JupyterHandler.prepare', new_callable=CoroutineMock)
    @patch('hsfiles_jupyter.handlers.upload_file_to_hydroshare', new_callable=CoroutineMock)
    @gen_test
    async def test_upload_file_handler(self, mock_upload, mock_prepare, mock_current_user):
        url = '/hydroshare/upload'
        await self.run_test(url=url, mock_function=mock_upload,
                            mock_return_value={"success": "File uploaded"}, mock_current_user=mock_current_user,
                            mock_prepare=mock_prepare)
        # await self.set_auth_cookies()
        # print(f">> Auth cookie: {self._auth_cookie}")
        # mock_current_user.return_value = "test_user"
        # mock_prepare.return_value = None
        # mock_upload.return_value = {"success": "File uploaded"}
        # response = await self.http_client.fetch(
        #     self.get_url('/hydroshare/upload'),
        #     method='POST',
        #     headers={
        #         "Content-Type": "application/json"
        #     },
        #     body=json.dumps({"path": "test_file_path"})
        # )
        # assert response.code == 200
        # assert json.loads(response.body) == {"response": {"success": "File uploaded"}}

    @patch('jupyter_server.base.handlers.JupyterHandler.current_user', new_callable=PropertyMock)
    @patch('jupyter_server.base.handlers.JupyterHandler.prepare', new_callable=CoroutineMock)
    @patch('hsfiles_jupyter.handlers.refresh_file_from_hydroshare', new_callable=CoroutineMock)
    @gen_test
    async def test_refresh_file_handler(self, mock_refresh, mock_prepare, mock_current_user):
        url = '/hydroshare/refresh'
        await self.run_test(url=url, mock_function=mock_refresh,
                            mock_return_value={"success": "File refreshed"}, mock_current_user=mock_current_user,
                            mock_prepare=mock_prepare)
        # await self.set_auth_cookies()
        # mock_current_user.return_value = "test_user"
        # mock_prepare.return_value = None
        # mock_refresh.return_value = {"success": "File refreshed"}
        # response = await self.http_client.fetch(
        #     self.get_url('/hydroshare/refresh'),
        #     method='POST',
        #     # headers={"Cookie": self._auth_cookie},
        #     headers={
        #         "Content-Type": "application/json"
        #     },
        #     body=json.dumps({"path": "test_file_path"})
        # )
        # assert response.code == 200
        # assert json.loads(response.body) == {"response": {"success": "File refreshed"}}

    @patch('jupyter_server.base.handlers.JupyterHandler.current_user', new_callable=PropertyMock)
    @patch('jupyter_server.base.handlers.JupyterHandler.prepare', new_callable=CoroutineMock)
    @patch('hsfiles_jupyter.handlers.delete_file_from_hydroshare', new_callable=CoroutineMock)
    @gen_test
    async def test_delete_file_handler(self, mock_delete, mock_prepare, mock_current_user):
        url = '/hydroshare/delete'
        await self.run_test(url=url, mock_function=mock_delete,
                            mock_return_value={"success": "File deleted"}, mock_current_user=mock_current_user,
                            mock_prepare=mock_prepare)
        # await self.set_auth_cookies()
        # mock_delete.return_value = {"success": "File deleted"}
        # response = await self.http_client.fetch(
        #     self.get_url('/hydroshare/delete'),
        #     method='POST',
        #     headers={"Cookie": self._auth_cookie},
        #     body=json.dumps({"path": "test_file_path"})
        # )
        # assert response.code == 200
        # assert json.loads(response.body) == {"response": {"success": "File deleted"}}

    @patch('jupyter_server.base.handlers.JupyterHandler.current_user', new_callable=PropertyMock)
    @patch('jupyter_server.base.handlers.JupyterHandler.prepare', new_callable=CoroutineMock)
    @patch('hsfiles_jupyter.handlers.check_file_status', new_callable=CoroutineMock)
    @gen_test
    async def test_check_file_status_handler(self, mock_check_status, mock_prepare, mock_current_user):
        url = '/hydroshare/status'
        await self.run_test(url=url, mock_function=mock_check_status,
                            mock_return_value={"success": "File exists"}, mock_current_user=mock_current_user,
                            mock_prepare=mock_prepare)
        # await self.set_auth_cookies()
        # mock_check_status.return_value = {"success": "File exists"}
        # response = await self.http_client.fetch(
        #     self.get_url('/hydroshare/status'),
        #     method='POST',
        #     headers={"Cookie": self._auth_cookie},
        #     body=json.dumps({"path": "test_file_path"})
        # )
        # assert response.code == 200
        # assert json.loads(response.body) == {"response": {"success": "File exists"}}