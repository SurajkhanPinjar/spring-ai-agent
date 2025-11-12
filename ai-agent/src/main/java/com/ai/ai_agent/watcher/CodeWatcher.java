package com.ai.ai_agent.watcher;

import com.ai.ai_agent.reviewer.AiReviewService;
import com.ai.ai_agent.testgen.AiTestGenerator;

import java.io.IOException;
import java.nio.file.*;
import static java.nio.file.StandardWatchEventKinds.*;

public class CodeWatcher {

    private static final Path WATCH_PATH =
            Paths.get("../app/src/main/java/com/ai_agent/app/service");

    public static void main(String[] args) throws IOException, InterruptedException {
        WatchService watchService = FileSystems.getDefault().newWatchService();
        WATCH_PATH.register(watchService, ENTRY_MODIFY);
        System.out.println("👀 Watching for code changes in: " + WATCH_PATH);
        System.out.println("📁 Absolute path: " + WATCH_PATH.toAbsolutePath());

        while (true) {
            WatchKey key = watchService.take();

            for (WatchEvent<?> event : key.pollEvents()) {
                if (event.kind() == ENTRY_MODIFY) {
                    String fileName = event.context().toString();
                    if (fileName.endsWith(".java")) {
                        Path filePath = WATCH_PATH.resolve(fileName);
                        System.out.println("🔁 File changed: " + fileName);
                        AiReviewService.reviewFile(filePath.toString());
                        AiTestGenerator.generateTests(filePath.toString());
                    }
                }
            }
            key.reset();
        }
    }
}