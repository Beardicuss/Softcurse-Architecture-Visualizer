import { shouldIgnorePath } from '../config/ignore-service';
import { FileEntry } from './zip';

/**
 * Read all files from a directory using the File System Access API (showDirectoryPicker)
 * Works in Chromium-based browsers including WebView2
 */
export const readDirectoryFromPicker = async (
  onProgress?: (message: string, percent: number) => void
): Promise<FileEntry[]> => {
  // @ts-ignore - showDirectoryPicker is not yet in TypeScript lib
  const dirHandle: FileSystemDirectoryHandle = await window.showDirectoryPicker({
    mode: 'read',
  });

  onProgress?.('Scanning directory...', 5);

  const files: FileEntry[] = [];
  const allEntries: { handle: FileSystemFileHandle; path: string }[] = [];

  // Recursively collect all file handles
  const collectFiles = async (handle: FileSystemDirectoryHandle, basePath: string) => {
    for await (const entry of handle.values()) {
      const entryPath = basePath ? `${basePath}/${entry.name}` : entry.name;

      if (entry.kind === 'directory') {
        // Skip common directories that should be ignored
        if (shouldIgnorePath(entryPath + '/')) continue;
        await collectFiles(entry as FileSystemDirectoryHandle, entryPath);
      } else {
        if (!shouldIgnorePath(entryPath)) {
          allEntries.push({ handle: entry as FileSystemFileHandle, path: entryPath });
        }
      }
    }
  };

  await collectFiles(dirHandle, '');
  onProgress?.(`Found ${allEntries.length} files, reading...`, 20);

  // Read files in batches for progress reporting
  const batchSize = 50;
  for (let i = 0; i < allEntries.length; i += batchSize) {
    const batch = allEntries.slice(i, i + batchSize);
    const results = await Promise.all(
      batch.map(async ({ handle, path }) => {
        try {
          const file = await handle.getFile();
          // Skip binary files (> 1MB or non-text mimetype)
          if (file.size > 1024 * 1024) return null;
          const content = await file.text();
          // Skip files with null bytes (binary)
          if (content.includes('\0')) return null;
          return { path, content };
        } catch {
          return null;
        }
      })
    );

    for (const result of results) {
      if (result) files.push(result);
    }

    const percent = Math.round(20 + ((i + batch.length) / allEntries.length) * 75);
    onProgress?.(`Reading files... ${Math.min(i + batchSize, allEntries.length)}/${allEntries.length}`, percent);
  }

  onProgress?.(`Loaded ${files.length} files`, 100);
  return files;
};

/**
 * Read all files from a dropped directory using DataTransfer webkitGetAsEntry API
 */
export const readDirectoryFromDrop = async (
  items: DataTransferItemList,
  onProgress?: (message: string, percent: number) => void
): Promise<FileEntry[]> => {
  const files: FileEntry[] = [];
  const allEntries: { entry: FileSystemFileEntry; path: string }[] = [];

  onProgress?.('Scanning dropped folder...', 5);

  // Recursively collect FileSystemEntry items
  const collectEntries = async (entry: FileSystemEntry, basePath: string) => {
    const entryPath = basePath ? `${basePath}/${entry.name}` : entry.name;

    if (entry.isDirectory) {
      if (shouldIgnorePath(entryPath + '/')) return;
      const dirEntry = entry as FileSystemDirectoryEntry;
      const reader = dirEntry.createReader();

      // readEntries may not return all entries in one call
      const readAll = (): Promise<FileSystemEntry[]> => {
        return new Promise((resolve) => {
          const results: FileSystemEntry[] = [];
          const readBatch = () => {
            reader.readEntries((entries) => {
              if (entries.length === 0) {
                resolve(results);
              } else {
                results.push(...entries);
                readBatch();
              }
            });
          };
          readBatch();
        });
      };

      const entries = await readAll();
      await Promise.all(entries.map(e => collectEntries(e, entryPath)));
    } else if (entry.isFile) {
      if (!shouldIgnorePath(entryPath)) {
        allEntries.push({ entry: entry as FileSystemFileEntry, path: entryPath });
      }
    }
  };

  // Get root entries from DataTransferItemList
  const rootEntries: FileSystemEntry[] = [];
  for (let i = 0; i < items.length; i++) {
    const entry = items[i].webkitGetAsEntry?.();
    if (entry) rootEntries.push(entry);
  }

  // If only one root directory, use its contents directly (strip root folder name)
  if (rootEntries.length === 1 && rootEntries[0].isDirectory) {
    const dirEntry = rootEntries[0] as FileSystemDirectoryEntry;
    const reader = dirEntry.createReader();

    const readAll = (): Promise<FileSystemEntry[]> => {
      return new Promise((resolve) => {
        const results: FileSystemEntry[] = [];
        const readBatch = () => {
          reader.readEntries((entries) => {
            if (entries.length === 0) {
              resolve(results);
            } else {
              results.push(...entries);
              readBatch();
            }
          });
        };
        readBatch();
      });
    };

    const entries = await readAll();
    await Promise.all(entries.map(e => collectEntries(e, '')));
  } else {
    await Promise.all(rootEntries.map(e => collectEntries(e, '')));
  }

  onProgress?.(`Found ${allEntries.length} files, reading...`, 20);

  // Read file contents
  const batchSize = 50;
  for (let i = 0; i < allEntries.length; i += batchSize) {
    const batch = allEntries.slice(i, i + batchSize);
    const results = await Promise.all(
      batch.map(({ entry, path }) => {
        return new Promise<FileEntry | null>((resolve) => {
          (entry as FileSystemFileEntry).file(
            async (file) => {
              try {
                if (file.size > 1024 * 1024) { resolve(null); return; }
                const content = await file.text();
                if (content.includes('\0')) { resolve(null); return; }
                resolve({ path, content });
              } catch {
                resolve(null);
              }
            },
            () => resolve(null)
          );
        });
      })
    );

    for (const result of results) {
      if (result) files.push(result);
    }

    const percent = Math.round(20 + ((i + batch.length) / allEntries.length) * 75);
    onProgress?.(`Reading files... ${Math.min(i + batchSize, allEntries.length)}/${allEntries.length}`, percent);
  }

  onProgress?.(`Loaded ${files.length} files`, 100);
  return files;
};
