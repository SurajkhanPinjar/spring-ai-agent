package com.ai.ai_agent;

import com.ai.ai_agent.watcher.CodeWatcher;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;

@SpringBootApplication
public class AiAgentApplication {

	public static void main(String[] args) throws IOException, InterruptedException {
		SpringApplication.run(AiAgentApplication.class, args);
		System.out.println("🤖 AI Agent started...");
		CodeWatcher.main(args);
	}

}
