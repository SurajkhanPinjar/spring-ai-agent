package com.ai.ai_agent.testgen;

import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.StringEntity;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class AiTestGenerator {

    private static final String AI_URL = "http://localhost:5000/generate-tests";
    private static final Path TEST_DIR =
            Paths.get("../app/src/test/java/com/ai_agent/app/test");

    /**
     * Sends Java code to the Python AI agent for generating JUnit tests.
     * Saves output as *Test.java in /reviewed/ folder.
     */
    public static void generateTests(String filePath) {
        try {
            String code = Files.readString(Paths.get(filePath));
            System.out.println("🧪 Sending file for AI test generation: " + filePath);

            try (CloseableHttpClient client = HttpClients.createDefault()) {
                HttpPost post = new HttpPost(AI_URL);
                post.setHeader("Content-Type", "text/plain");
                post.setEntity(new StringEntity(code, StandardCharsets.UTF_8));

                // Execute and get AI response
                String response = client.execute(post, httpResponse ->
                        new String(httpResponse.getEntity().getContent().readAllBytes(), StandardCharsets.UTF_8));

                saveTestFile(filePath, response);
            }
        } catch (Exception e) {
            System.err.println("❌ Failed to generate tests for " + filePath);
            e.printStackTrace();
        }
    }

    private static void saveTestFile(String filePath, String content) throws IOException {
        Files.createDirectories(TEST_DIR);
        String fileName = Paths.get(filePath).getFileName().toString();
        Path testFile = TEST_DIR.resolve(fileName.replace(".java", "Test.java"));
        Files.writeString(testFile, content, StandardCharsets.UTF_8);
        System.out.println("💾 Saved AI-generated test: " + testFile);
    }
}