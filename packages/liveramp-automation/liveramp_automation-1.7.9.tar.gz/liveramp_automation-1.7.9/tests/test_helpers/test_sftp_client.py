from unittest import TestCase
from unittest.mock import MagicMock, patch

import paramiko

from liveramp_automation.helpers.sftp_client import SFTPClient


class TestSFTPClient(TestCase):
    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_connection_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        cnopts = {"look_for_keys": False}
        with SFTPClient(
            username="user", password="pass", hostname="host", cnopts=cnopts
        ) as client:
            self.assertIsNotNone(client.sftp)
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="user",
                password="pass",
                key_filename=None,
                passphrase=None,
                **cnopts,
            )
            mock_ssh.set_missing_host_key_policy.assert_called_once()
            mock_ssh.get_transport.assert_called_once()
            mock_transport.open_sftp_client.assert_called_once()

        mock_logger.info.assert_any_call("Successfully connected to host")
        mock_logger.info.assert_any_call("Disconnected from host")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_context_manager_connection_failure(self, mock_ssh_client):
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_ssh.connect.side_effect = paramiko.ssh_exception.AuthenticationException(
            "Auth failed"
        )

        with self.assertRaises(paramiko.ssh_exception.AuthenticationException):
            with SFTPClient(username="user", password="pass"):
                pass

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with patch("os.path.dirname", return_value=""), patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file("remote.txt", "local.txt")
                self.assertTrue(result)
                mock_sftp.get.assert_called_once_with(
                    remotepath="remote.txt", localpath="local.txt"
                )
        mock_logger.info.assert_any_call("SFTP Download successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_file_failure(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.get.side_effect = Exception("Download error")

        with patch("os.path.dirname", return_value=""), patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_file("remote.txt", "local.txt")
                self.assertFalse(result)
        mock_logger.error.assert_called_with("Error downloading file: Download error")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_success(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertTrue(result)
            mock_sftp.put.assert_called_once_with(
                localpath="local.txt", remotepath="remote.txt"
            )
        mock_logger.info.assert_any_call("SFTP Upload successful")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_file_failure(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.put.side_effect = Exception("Upload error")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            result = client.upload_file("local.txt", "remote.txt")
            self.assertFalse(result)
        mock_logger.error.assert_called_with("Error uploading file: Upload error")

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return file mode (not directory)
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, ["file1.txt", "file2.txt"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_files_failure(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp
        mock_sftp.listdir.side_effect = Exception("List error")

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            files = client.list_files("remote_dir")
            self.assertEqual(files, [])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_list_directories_success(self, mock_ssh_client):
        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock stat to return directory mode for specific paths
        def mock_stat_side_effect(path):
            mock_stat = MagicMock()
            if "dir1" in path:
                mock_stat.st_mode = 0o40755  # Directory mode (0o40000 | 0o755)
            else:
                mock_stat.st_mode = 0o644  # Regular file mode
            return mock_stat

        mock_sftp.stat.side_effect = mock_stat_side_effect
        mock_sftp.listdir.return_value = ["dir1", "file1.txt"]

        with SFTPClient(username="user", password="pass", hostname="host") as client:
            directories = client.list_directories("remote_dir")
            self.assertEqual(directories, ["dir1"])

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_upload_directory_simple(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.stat.side_effect = FileNotFoundError()
        mock_sftp.mkdir.return_value = None

        with (
            patch("os.listdir", return_value=["file1.txt", "file2.txt"]),
            patch("os.path.isfile", return_value=True),
            patch("os.path.join", side_effect=lambda *args: "/".join(args)),
        ):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.upload_directory(
                    "/local/dir", "/remote/dir", recursive=False
                )
                self.assertTrue(result)
                mock_sftp.mkdir.assert_called_once_with("/remote/dir")
                self.assertEqual(mock_sftp.put.call_count, 2)

    @patch("liveramp_automation.helpers.sftp_client.paramiko.SSHClient")
    def test_download_directory_simple(self, mock_ssh_client):
        mock_logger = patch("liveramp_automation.helpers.sftp_client.Logger").start()

        # Setup mocks
        mock_ssh = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh.get_transport.return_value = mock_transport
        mock_transport.open_sftp_client.return_value = mock_sftp

        # Mock directory operations
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o644  # Regular file mode
        mock_sftp.stat.return_value = mock_stat

        with patch("os.makedirs"):
            with SFTPClient(
                username="user", password="pass", hostname="host"
            ) as client:
                result = client.download_directory(
                    "/remote/dir", "/local/dir", recursive=False
                )
                self.assertTrue(result)
                self.assertEqual(mock_sftp.get.call_count, 2)
