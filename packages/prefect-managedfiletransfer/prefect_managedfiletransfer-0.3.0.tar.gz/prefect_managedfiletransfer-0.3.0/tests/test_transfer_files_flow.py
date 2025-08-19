from prefect_managedfiletransfer import FileMatcher, TransferType, transfer_files_flow
from prefect.filesystems import LocalFileSystem
import pytest

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_transfer_files_flow_can_copy_locally(
    prefect_db, temp_folder_path, temp_file_path
):
    source = LocalFileSystem(basepath=temp_file_path.parent)
    destination = LocalFileSystem(basepath=temp_folder_path)
    assert source.basepath != destination.basepath

    result = await transfer_files_flow(
        source_block=source,
        destination_block=destination,
        source_file_matchers=[
            FileMatcher(
                source_folder=temp_file_path.parent,
                pattern_to_match=temp_file_path.name,
            )
        ],
        mode=TransferType.Copy,
        check_for_space_overhead=1024 * 1024 * 10,
    )

    assert len(result) == 1
    assert temp_folder_path.joinpath(temp_file_path.name).exists(), (
        "File should be copied to destination folder"
    )


@pytest.mark.asyncio
async def test_transfer_files_flow_can_move_locally(
    prefect_db, temp_folder_path, temp_file_path
):
    source = LocalFileSystem(basepath=temp_file_path.parent)
    destination = LocalFileSystem(basepath=temp_folder_path)
    assert source.basepath != destination.basepath

    result = await transfer_files_flow(
        source_block=source,
        destination_block=destination,
        source_file_matchers=[
            FileMatcher(
                source_folder=temp_file_path.parent,
                pattern_to_match=temp_file_path.name,
            )
        ],
        mode=TransferType.Move,
        check_for_space=False,
    )

    assert len(result) == 1
    assert not temp_file_path.exists(), "File should be moved from source folder"
    assert temp_folder_path.joinpath(temp_file_path.name).exists(), (
        "File should be moved to destination folder"
    )


@pytest.mark.asyncio
async def test_transfer_files_flow_can_ignore_files(
    prefect_db, temp_folder_path, temp_file_path
):
    source = LocalFileSystem(basepath=temp_file_path.parent)
    destination = LocalFileSystem(basepath=temp_folder_path)
    assert source.basepath != destination.basepath

    result = await transfer_files_flow(
        source_block=source,
        destination_block=destination,
        source_file_matchers=[
            FileMatcher(
                source_folder=temp_file_path.parent, pattern_to_match="Not-a-file"
            )
        ],
        mode=TransferType.Move,
    )

    assert len(result) == 0
    assert temp_file_path.exists(), "File should NOT be moved from source folder"
    assert not temp_folder_path.joinpath(temp_file_path.name).exists(), (
        "File should not be moved to destination folder"
    )
