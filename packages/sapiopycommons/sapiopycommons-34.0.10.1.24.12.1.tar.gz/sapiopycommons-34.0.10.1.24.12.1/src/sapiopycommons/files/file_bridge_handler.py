from __future__ import annotations

from abc import abstractmethod, ABC
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser

from sapiopycommons.files.file_bridge import FileBridge
from sapiopycommons.general.aliases import AliasUtil, UserIdentifier


class FileBridgeHandler:
    """
    The FileBridgeHandler provides caching of the results of file bridge endpoint calls while also containing quality
    of life functions for common file bridge actions.
    """
    user: SapioUser
    __bridge: str
    __file_cache: dict[str, bytes]
    """A cache of file paths to file bytes."""
    __files: dict[str, File]
    """A cache of file paths to File objects."""
    __dir_cache: dict[str, list[str]]
    """A cache of directory file paths to the names of the files or nested directories within it."""
    __directories: dict[str, Directory]
    """A cache of directory file paths to Directory objects."""

    __instances: WeakValueDictionary[str, FileBridgeHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier, bridge_name: str):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        user = AliasUtil.to_sapio_user(context)
        key = f"{user.__hash__()}:{bridge_name}"
        obj = cls.__instances.get(key)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[key] = obj
        return obj

    def __init__(self, context: UserIdentifier, bridge_name: str):
        """
        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to communicate with. This is the "connection name" in the
            file bridge configurations.
        """
        if self.__initialized:
            return
        self.__initialized = True

        self.user = AliasUtil.to_sapio_user(context)
        self.__bridge = bridge_name
        self.__file_cache = {}
        self.__files = {}
        self.__dir_cache = {}
        self.__directories = {}

    @property
    def connection_name(self) -> str:
        return self.__bridge

    def clear_caches(self) -> None:
        """
        Clear the file and directory caches of this handler.
        """
        self.__file_cache.clear()
        self.__files.clear()
        self.__dir_cache.clear()
        self.__directories.clear()

    def read_file(self, file_path: str, base64_decode: bool = True) -> bytes:
        """
        Read a file from FileBridge. The bytes of the given file will be cached so that any subsequent reads of this
        file will not make an additional webservice call.

        :param file_path: The path to read the file from.
        :param base64_decode: If true, base64 decode the file. Files are by default base64 encoded when retrieved from
            FileBridge.
        :return: The bytes of the file.
        """
        if file_path in self.__file_cache:
            return self.__file_cache[file_path]
        file_bytes: bytes = FileBridge.read_file(self.user, self.__bridge, file_path, base64_decode)
        self.__file_cache[file_path] = file_bytes
        return file_bytes

    def write_file(self, file_path: str, file_data: bytes | str) -> None:
        """
        Write a file to FileBridge. The bytes of the given file will be cached so that any subsequent reads of this
        file will not make an additional webservice call.

        :param file_path: The path to write the file to. If a file already exists at the given path then the file is
            overwritten.
        :param file_data: A string or bytes of the file to be written.
        """
        FileBridge.write_file(self.user, self.__bridge, file_path, file_data)
        self.__file_cache[file_path] = file_data if isinstance(file_data, bytes) else file_data.encode()

        # Find the directory path to this file and the name of the file. Add the file name to the cached list of
        # files for the directory, assuming we have this directory cached and the file isn't already in it.
        last_slash: int = file_path.rfind("/")
        dir_path: str = file_path[:last_slash]
        file_name: str = file_path[last_slash + 1:]
        if dir_path in self.__dir_cache and file_path not in self.__dir_cache[dir_path]:
            self.__dir_cache[dir_path].append(file_name)

    def delete_file(self, file_path: str) -> None:
        """
        Delete an existing file in FileBridge. If this file is in the cache, it will also be deleted from the cache.

        :param file_path: The path to the file to delete.
        """
        FileBridge.delete_file(self.user, self.__bridge, file_path)
        if file_path in self.__file_cache:
            self.__file_cache.pop(file_path)
        if file_path in self.__files:
            self.__files.pop(file_path)

    def list_directory(self, file_path: str) -> list[str]:
        """
        List the contents of a FileBridge directory. The contents of this directory will be cached so that any
        subsequent lists of this directory will not make an additional webservice call.

        :param file_path: The path to read the directory from.
        :return: A list of names of files and folders in the directory.
        """
        if file_path in self.__dir_cache:
            return self.__dir_cache[file_path]
        files: list[str] = FileBridge.list_directory(self.user, self.__bridge, file_path)
        self.__dir_cache[file_path] = files
        return files

    def create_directory(self, file_path: str) -> None:
        """
        Create a new directory in FileBridge. This new directory will be added to the cache as empty so that listing
        the same directory does not make an additional webservice call.

        :param file_path: The path to create the directory at. If a directory already exists at the given path then an
            exception is raised.
        """
        FileBridge.create_directory(self.user, self.__bridge, file_path)
        # This directory was just created, so we know it's empty.
        self.__dir_cache[file_path] = []

    def delete_directory(self, file_path: str) -> None:
        """
        Delete an existing directory in FileBridge. If this directory is in the cache, it will also be deleted
        from the cache.

        :param file_path: The path to the directory to delete.
        """
        FileBridge.delete_directory(self.user, self.__bridge, file_path)
        if file_path in self.__dir_cache:
            self.__dir_cache.pop(file_path)
        if file_path in self.__directories:
            self.__directories.pop(file_path)

    def is_file(self, file_path: str) -> bool:
        """
        Determine if the given file path points to a file or a directory. This is achieved by trying to call
        list_directory on the given file path. If an exception is thrown, that's because the function was called
        on a file. If no exception is thrown, then we know that this is a directory, and we have now also cached
        the contents of that directory if it wasn't cached already.

        :param file_path: A file path.
        :return: True if the file path points to a file. False if it points to a directory.
        """
        try:
            self.list_directory(file_path)
            return False
        except Exception:
            return True

    def move_file(self, move_from: str, move_to: str, old_name: str, new_name: str | None = None) -> None:
        """
        Move a file from one location to another within File Bridge. This is done be reading the file into memory,
        writing a copy of the file in the new location, then deleting the original file.

        :param move_from: The path to the current location of the file.
        :param move_to: The path to move the file to.
        :param old_name: The current name of the file.
        :param new_name: The name that the file should have after it is moved. if this is not provided, then the new
            name will be the same as the old name.
        """
        if not new_name:
            new_name = old_name

        # Read the file into memory.
        file_bytes: bytes = self.read_file(move_from + "/" + old_name)
        # Write the file into the new location.
        self.write_file(move_to + "/" + new_name, file_bytes)
        # Delete the file from the old location. We do this last in case the write call fails.
        self.delete_file(move_from + "/" + old_name)

    def get_file_object(self, file_path: str) -> File:
        """
        Get a File object from a file path. This object can be used to get the contents of the file at this path
        and traverse up the file hierarchy to the directory that the file is contained within.

        There is no guarantee that this file actually exists within the current file bridge connection when it is
        constructed. If the file doesn't exist, then retrieving its contents will fail.

        :param file_path: A file path.
        :return: A File object constructed form the given file path.
        """
        if file_path in self.__files:
            return self.__files[file_path]
        file = File(self, file_path)
        self.__files[file_path] = file
        return file

    def get_directory_object(self, file_path: str) -> Directory | None:
        """
        Get a Directory object from a file path. This object can be used to traverse up and down the file hierarchy
        by going up to the parent directory that this directory is contained within or going down to the contents of
        this directory.

        There is no guarantee that this directory actually exists within the current file bridge connection when it is
        constructed. If the directory doesn't exist, then retrieving its contents will fail.

        :param file_path: A file path.
        :return: A Directory object constructed form the given file path.
        """
        if file_path is None:
            return None
        if file_path in self.__directories:
            return self.__directories[file_path]
        directory = Directory(self, file_path)
        self.__directories[file_path] = directory
        return directory


class FileBridgeObject(ABC):
    """
    A FileBridgeObject is either a file or a directory that is contained within file bridge. Every object has a
    name and a parent directory that it is contained within (unless the object is located in the bridge root, in
    which case the parent is None). From the name and the parent, a path can be constructed to that object.
    """
    _handler: FileBridgeHandler
    name: str
    parent: Directory | None

    def __init__(self, handler: FileBridgeHandler, file_path: str):
        self._handler = handler

        name, root = split_path(file_path)
        self.name = name
        self.parent = handler.get_directory_object(root)

    @abstractmethod
    def is_file(self) -> bool:
        """
        :return: True if this object is a file. False if it is a directory.
        """
        pass

    def get_path(self) -> str:
        """
        :return: The file path that leads to this object.
        """
        if self.parent is None:
            return self.name
        return self.parent.get_path() + "/" + self.name


class File(FileBridgeObject):
    def __init__(self, handler: FileBridgeHandler, file_path: str):
        """
        :param handler: A FileBridgeHandler for the connection that this file came from.
        :param file_path: The path to this file.
        """
        super().__init__(handler, file_path)

    @property
    def contents(self) -> bytes:
        """
        :return: The bytes of this file.
            This pulls from the cache of this object's related FileBridgeHandler.
        """
        return self._handler.read_file(self.get_path())

    def is_file(self) -> bool:
        return True


class Directory(FileBridgeObject):
    def __init__(self, handler: FileBridgeHandler, file_path: str):
        """
        :param handler: A FileBridgeHandler for the connection that this directory came from.
        :param file_path: The path to this directory.
        """
        super().__init__(handler, file_path)

    @property
    def contents(self) -> dict[str, FileBridgeObject]:
        """
        :return: A dictionary of object names to the objects (Files or Directories) contained within this Directory.
            This pulls from the cache of this object's related FileBridgeHandler.
        """
        contents: dict[str, FileBridgeObject] = {}
        path: str = self.get_path()
        for name in self._handler.list_directory(path):
            file_path: str = path + "/" + name
            if self._handler.is_file(file_path):
                contents[name] = self._handler.get_file_object(file_path)
            else:
                contents[name] = self._handler.get_directory_object(file_path)
        return contents

    def is_file(self) -> bool:
        return False

    def get_files(self) -> dict[str, File]:
        """
        :return: A mapping of file name to File for every file in this Directory.
            This pulls from the cache of this object's related FileBridgeHandler.
        """
        return {x: y for x, y in self.contents.items() if y.is_file()}

    def get_directories(self) -> dict[str, Directory]:
        """
        :return: A mapping of directory name to Directory for every directory in this Directory.
            This pulls from the cache of this object's related FileBridgeHandler.
        """
        return {x: y for x, y in self.contents.items() if not y.is_file()}


def split_path(file_path: str) -> tuple[str, str]:
    """
    :param file_path: A file path where directories are separated the "/" characters.
    :return: A tuple of two strings that splits the path on its last slash. The first string is the name of the
        file/directory at the given file path and the second string is the location to that file.
    """
    last_slash: int = file_path.rfind("/")
    if last_slash == -1:
        return file_path, None
    return file_path[last_slash + 1:], file_path[:last_slash]
