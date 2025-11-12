package com.ai.ai_agent.reviewer;

import java.io.*;
import org.apache.hc.client5.http.classic.methods.*;
import org.apache.hc.client5.http.impl.classic.*;
import org.apache.hc.core5.http.io.entity.StringEntity;

public class CodeReviewer {

    public static void reviewFile(String filePath) {
        try {
            String code = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(filePath)));

            try (CloseableHttpClient client = HttpClients.createDefault()) {
                HttpPost post = new HttpPost("http://localhost:5000/review");
                post.setEntity(new StringEntity(code));
                post.setHeader("Content-Type", "application/json");
                client.execute(post);
                System.out.println("📤 Sent file for AI review: " + filePath);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}