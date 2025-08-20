import os
from unittest.mock import MagicMock, patch

import pytest
from hsclient.hydroshare import File

from hsfiles_jupyter.refresh_file import refresh_file_from_hydroshare
from hsfiles_jupyter.utils import HydroShareAuthError


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_success():
    """Test successful file refresh from HydroShare."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_hydroshare_resource_info
        mock_res_info = MagicMock()
        mock_res_info.resource_id = "15723969f1d7494883ef5ad5845aac5f"
        mock_res_info.hs_file_path = "example.txt"
        mock_res_info.hs_file_relative_path = "example.txt"

        # Create File object for testing
        mock_file = File("example.txt", "http://example.com/example.txt", "abc123")
        mock_res_info.files = [mock_file]  # File exists in HydroShare

        mock_res_info.resource = MagicMock()
        mock_res_info.refresh = False

        # Mock resource.file() to return the File object
        mock_res_info.resource.file.return_value = mock_file

        mock_rfc_manager.get_hydroshare_resource_info.return_value = mock_res_info

        # Mock get_local_absolute_file_path
        with patch("hsfiles_jupyter.refresh_file.get_local_absolute_file_path") as mock_get_path:
            mock_get_path.return_value = "/tmp"

            # Call the function
            result = await refresh_file_from_hydroshare(file_path)

            # Verify the result
            assert "success" in result
            assert mock_res_info.resource_id in result["success"]
            assert mock_res_info.hs_file_path in result["success"]

            # Verify the mocks were called correctly
            mock_rfc_manager.get_hydroshare_resource_info.assert_called_once_with(file_path)
            mock_get_path.assert_called_once_with(os.path.dirname(file_path))
            mock_res_info.resource.file_download.assert_called_once_with(
                path=mock_res_info.hs_file_relative_path, save_path=mock_get_path.return_value
            )


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_auth_error():
    """Test file refresh with authentication error."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_hydroshare_resource_info to raise HydroShareAuthError
        mock_rfc_manager.get_hydroshare_resource_info.side_effect = HydroShareAuthError("Auth error")

        # Call the function
        result = await refresh_file_from_hydroshare(file_path)

        # Verify the result
        assert "error" in result
        assert "Auth error" in result["error"]


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_file_not_found():
    """Test file refresh when file is not found in HydroShare."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_hydroshare_resource_info
        mock_res_info = MagicMock()
        mock_res_info.resource_id = "15723969f1d7494883ef5ad5845aac5f"
        mock_res_info.hs_file_path = "example.txt"
        mock_res_info.hs_file_relative_path = "example.txt"
        mock_res_info.files = []  # File doesn't exist in HydroShare
        mock_res_info.refresh = True  # Already refreshed
        mock_res_info.resource = MagicMock()

        # Mock resource.file() to return None (file not found)
        mock_res_info.resource.file.return_value = None

        mock_rfc_manager.get_hydroshare_resource_info.return_value = mock_res_info

        # Call the function
        result = await refresh_file_from_hydroshare(file_path)

        # Verify the result
        assert "error" in result
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_file_not_found_with_refresh():
    """Test file refresh when file is not found in HydroShare, even after refreshing."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_hydroshare_resource_info
        mock_res_info = MagicMock()
        mock_res_info.resource_id = "15723969f1d7494883ef5ad5845aac5f"
        mock_res_info.hs_file_path = "example.txt"
        mock_res_info.hs_file_relative_path = "example.txt"
        mock_res_info.files = []  # File doesn't exist in HydroShare
        mock_res_info.refresh = False  # Not refreshed yet
        mock_res_info.resource = MagicMock()
        mock_rfc_manager.get_hydroshare_resource_info.return_value = mock_res_info

        # Create File object for other file (not the one we're looking for)
        other_file = File("other_file.txt", "http://example.com/other_file.txt", "def456")

        # Mock get_files to return a list not containing our file
        mock_rfc_manager.get_files.return_value = ([other_file], True)

        # Mock resource.file() to return None (file not found)
        mock_res_info.resource.file.return_value = None

        # Call the function
        result = await refresh_file_from_hydroshare(file_path)

        # Verify the result
        assert "error" in result
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_download_error():
    """Test file refresh with an error during download."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock the ResourceFileCacheManager
    with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
        mock_rfc_manager = MagicMock()
        mock_rfc_manager_class.return_value = mock_rfc_manager

        # Mock get_hydroshare_resource_info
        mock_res_info = MagicMock()
        mock_res_info.resource_id = "15723969f1d7494883ef5ad5845aac5f"
        mock_res_info.hs_file_path = "example.txt"
        mock_res_info.hs_file_relative_path = "example.txt"

        # Create File object for testing
        mock_file = File("example.txt", "http://example.com/example.txt", "abc123")
        mock_res_info.files = [mock_file]  # File exists in HydroShare

        mock_res_info.resource = MagicMock()
        mock_res_info.refresh = False

        # Mock resource.file() to return the File object
        mock_res_info.resource.file.return_value = mock_file

        mock_rfc_manager.get_hydroshare_resource_info.return_value = mock_res_info

        # Mock get_local_absolute_file_path
        with patch("hsfiles_jupyter.refresh_file.get_local_absolute_file_path") as mock_get_path:
            mock_get_path.return_value = "/tmp"

            # Mock file_download to raise an exception
            mock_res_info.resource.file_download.side_effect = Exception("Download failed")

            # Call the function
            result = await refresh_file_from_hydroshare(file_path)

            # Verify the result
            assert "error" in result
            assert "Failed to replace file" in result["error"]
            assert "Download failed" in result["error"]


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_file_not_in_download_dir_error():
    """Test file refresh when file is not in the designated download directory."""
    file_path = "tmp/Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock get_hydroshare_resource_download_dir to return "Downloads"
    with patch("hsfiles_jupyter.utils.get_hydroshare_resource_download_dir") as mock_download_dir:
        mock_download_dir.return_value = "Downloads"

        # Call the function (should get validation error)
        result = await refresh_file_from_hydroshare(file_path)

        # Verify we get an error for path validation
        assert "error" in result
        assert "is not within the HydroShare download directory" in result["error"]


@pytest.mark.asyncio
async def test_refresh_file_from_hydroshare_file_in_correct_download_dir():
    """Test file refresh when file is in the correct download directory."""
    file_path = "Downloads/15723969f1d7494883ef5ad5845aac5f/data/contents/example.txt"

    # Mock get_hydroshare_resource_download_dir to return "Downloads"
    with patch("hsfiles_jupyter.utils.get_hydroshare_resource_download_dir") as mock_download_dir:
        mock_download_dir.return_value = "Downloads"

        # Mock the ResourceFileCacheManager
        with patch("hsfiles_jupyter.refresh_file.ResourceFileCacheManager") as mock_rfc_manager_class:
            mock_rfc_manager = MagicMock()
            mock_rfc_manager_class.return_value = mock_rfc_manager

            # Mock get_hydroshare_resource_info - should pass validation
            mock_res_info = MagicMock()
            mock_res_info.resource_id = "15723969f1d7494883ef5ad5845aac5f"
            mock_res_info.hs_file_path = "data/contents/example.txt"
            mock_res_info.hs_file_relative_path = "data/contents/example.txt"

            # Create File object for testing
            mock_file = File("data/contents/example.txt", "http://example.com/data/contents/example.txt", "abc123")
            mock_res_info.files = [mock_file]  # File exists in HydroShare

            mock_res_info.resource = MagicMock()
            mock_res_info.refresh = False

            # Mock resource.file() to return the File object
            mock_res_info.resource.file.return_value = mock_file

            mock_rfc_manager.get_hydroshare_resource_info.return_value = mock_res_info

            # Mock get_local_absolute_file_path
            with patch("hsfiles_jupyter.refresh_file.get_local_absolute_file_path") as mock_get_path:
                mock_get_path.return_value = "/tmp"

                # Call the function
                result = await refresh_file_from_hydroshare(file_path)

                # Verify we get success (not a validation error)
                assert "success" in result
                assert mock_res_info.resource_id in result["success"]
                assert mock_res_info.hs_file_path in result["success"]

                # Verify the mocks were called correctly
                mock_rfc_manager.get_hydroshare_resource_info.assert_called_once_with(file_path)
                mock_get_path.assert_called_once_with(os.path.dirname(file_path))
                mock_res_info.resource.file_download.assert_called_once_with(
                    path=mock_res_info.hs_file_relative_path, save_path=mock_get_path.return_value
                )
