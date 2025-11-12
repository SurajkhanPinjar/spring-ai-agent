package com.ai.ai_agent.watcher;

import com.ai.ai_agent.reviewer.CodeReviewer;

import java.io.IOException;
import java.nio.file.*;


public class CodeWatcher {

    public static void main(String[] args) throws IOException, InterruptedException {
        Path path = Paths.get("../spring-app/src/main/java/com/example/app/service");
        WatchService watchService = FileSystems.getDefault().newWatchService();
        path.register(watchService, StandardWatchEventKinds.ENTRY_MODIFY);

        System.out.println("👀 Watching for file changes in: " + path);

        WatchKey key;
        while ((key = watchService.take()) != null) {
            for (WatchEvent<?> event : key.pollEvents()) {
                String fileName = event.context().toString();
                if (fileName.endsWith(".java")) {
                    System.out.println("🧩 Modified: " + fileName);
                    CodeReviewer.reviewFile(path.resolve(fileName).toString());
                }
            }
            key.reset();
        }
    }
}