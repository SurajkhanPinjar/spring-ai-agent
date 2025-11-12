package com.ai.ai_agent.reviewer;

import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.StringEntity;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class AiReviewService {

    // 🔹 Flask AI server endpoint (Python AI Agent)
    private static final String AI_URL = "http://localhost:5000/review";

    // 🔹 Corrected path — matches your folder structure
    // ai-agent -> app (Spring Boot module)
    private static final Path REVIEWED_DIR =
            Paths.get("../app/src/main/java/com/ai_agent/app/reviewed");

    /**
     * Sends a Java file's content to the Python AI Agent for code review.
     * Saves the AI-reviewed output in /reviewed directory.
     */
    public static void reviewFile(String filePath) {
        try {
            String code = Files.readString(Paths.get(filePath));
            System.out.println("🧠 Sending file for AI review: " + filePath);

            try (CloseableHttpClient client = HttpClients.createDefault()) {
                HttpPost post = new HttpPost(AI_URL);
                post.setHeader("Content-Type", "text/plain");
                post.setEntity(new StringEntity(code, StandardCharsets.UTF_8));

                // Execute request and get AI response
                String response = client.execute(post, httpResponse ->
                        new String(httpResponse.getEntity().getContent().readAllBytes(), StandardCharsets.UTF_8));

                // Save AI-reviewed output
                saveReviewedFile(filePath, response);
            }
        } catch (Exception e) {
            System.err.println("❌ Failed to review file " + filePath);
            e.printStackTrace();
        }
    }

    /**
     * Saves reviewed AI code into the /reviewed directory inside the Spring app.
     */
    private static void saveReviewedFile(String filePath, String content) throws IOException {
        Files.createDirectories(REVIEWED_DIR);

        String fileName = Paths.get(filePath).getFileName().toString();
        Path reviewedFile = REVIEWED_DIR.resolve(fileName.replace(".java", "_Reviewed.java"));

        Files.writeString(reviewedFile, content, StandardCharsets.UTF_8);
        System.out.println("💾 Saved reviewed file: " + reviewedFile);
    }
}