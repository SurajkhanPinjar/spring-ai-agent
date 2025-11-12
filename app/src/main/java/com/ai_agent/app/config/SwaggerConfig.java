package com.ai_agent.app.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI apiInfo() {
        return new OpenAPI()
                .info(new Info()
                        .title("AI Agent API")
                        .description("Spring Boot REST API documentation for AI Agent Service")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Suraj Khan Pinjar")
                                .email("suraj@example.com")
                                .url("https://github.com/surajkhanpinjar"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("http://springdoc.org")));
    }
}