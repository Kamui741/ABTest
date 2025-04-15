/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:07:56
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:40:27
 * @FilePath: src/main/java/com/example/abtest/adapter/ExperimentAdapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import java.util.Map;

public interface ExperimentAdapter {
    // 补充所有必要的方法声明
    Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params);
    Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response);
    Map<String, Object> convertGetDetailsRequest(Map<String, Object> params);
    Map<String, Object> convertGetDetailsResponse(Map<String, Object> response);
    Map<String, Object> convertGenerateReportRequest(Map<String, Object> params);
    Map<String, Object> convertGenerateReportResponse(Map<String, Object> response);
    Map<String, Object> convertModifyStatusRequest(Map<String, Object> params);
    Map<String, Object> convertModifyStatusResponse(Map<String, Object> response);
    Map<String, Object> convertListMetricsRequest(Map<String, Object> params);
    Map<String, Object> convertListMetricsResponse(Map<String, Object> response);
    Map<String, Object> convertListGroupsRequest(Map<String, Object> params);
    Map<String, Object> convertListGroupsResponse(Map<String, Object> response);
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:54:37
 * @FilePath: src/main/java/com/example/abtest/adapter/V1Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.ExperimentAdapter;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.Map;


@Component
public class V1Adapter implements ExperimentAdapter {

    @Override
    public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
        params.put("hash_strategy", "ssid");
        return params;
    }

    @Override
    public Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGetDetailsRequest(Map<String, Object> params) {
        params.put("is_duplicate", false);
        return params;
    }

    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    // 其他转换方法实现...
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:07:08
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:45:59
 * @FilePath: src/main/java/com/example/abtest/adapter/V2Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.Map;

@Component
public class V2Adapter implements ExperimentAdapter {
    @Override
    public Map<String, Object> convertRequest(Map<String, Object> params) {
        return params; // 透传逻辑
    }

    @Override
    public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGetDetailsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }
}
package com.example.abtest.auth; /**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:52:28
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:45:59
 * @FilePath: src/main/java/com/example/abtest/auth/AuthUtils.java
 * @Description:
 */
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.Map;

public class AuthUtils {
    // 认证类型枚举
    public enum AuthType { V1, V2 }

    // 认证上下文管理
    @Component
    public static class AuthContext {
        private final V1Auth v1Auth;
        private final V2Auth v2Auth;

        public AuthContext(V1Auth v1Auth, V2Auth v2Auth) {
            this.v1Auth = v1Auth;
            this.v2Auth = v2Auth;
        }

        public Map<String, String> getAuthHeaders(AuthType type) {
            return switch (type) {
                case V1 -> v1Auth.getHeaders();
                case V2 -> v2Auth.getHeaders();
            };
        }
    }

    // RestTemplate配置
    @Configuration
    public static class AuthConfig {
        @Bean
        public RestTemplate restTemplate() {
            return new RestTemplateBuilder()
                    .setConnectTimeout(Duration.ofSeconds(5))
                    .build();
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:25:50
 * @FilePath: src/main/java/com/example/abtest/auth/V1Auth.java
 * @Description:
 */
package com.example.abtest.auth;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.time.Duration;
import java.util.Map;

// src/main/java/com/example/abtest/auth/V1AuthProvider.java
// ---------------------- V1Auth.java ----------------------
@Component
@Slf4j
public class V1Auth {
    private String sessionId;
    private final String sessionFile;
    private final String loginUrl;
    private final String username;
    private final String password;
    private final RestTemplate restTemplate;

    public V1Auth(
            @Value("${abtest.v1.session-file}") String sessionFile,
            @Value("${abtest.v1.login-url}") String loginUrl,
            @Value("${abtest.v1.username}") String username,
            @Value("${abtest.v1.password}") String password,
            RestTemplateBuilder restTemplateBuilder) {

        this.sessionFile = sessionFile;
        this.loginUrl = loginUrl;
        this.username = username;
        this.password = password;
        this.restTemplate = restTemplateBuilder.build();
        loadSession();
    }

    public Map<String, String> getHeaders() {
        if (!validateSession()) {
            refreshSession();
        }
        return Map.of("Cookie", "sessionid=" + sessionId);
    }

    private void loadSession() {
        try {
            if (new File(sessionFile).exists()) {
                sessionId = Files.readString(Path.of(sessionFile)).trim();
            }
        } catch (IOException e) {
            log.warn("Session load failed: {}", e.getMessage());
        }
    }

    private boolean validateSession() {
        try {
            return restTemplate.getForEntity("/validate", String.class)
                    .getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            return false;
        }
    }

    private synchronized void refreshSession() {
        try {
            ResponseEntity<Void> response = restTemplate.postForEntity(
                    loginUrl,
                    Map.of("email", username, "password", password),
                    Void.class
            );

            response.getHeaders().get("Set-Cookie").stream()
                    .filter(c -> c.startsWith("sessionid="))
                    .findFirst()
                    .ifPresent(cookie -> {
                        sessionId = cookie.split(";")[0].split("=")[1];
                        saveSessionToFile();
                    });
        } catch (Exception e) {
            throw new RuntimeException("V1 login failed", e);
        }
    }

    private void saveSessionToFile() {
        try {
            Files.writeString(Path.of(sessionFile), sessionId);
        } catch (IOException e) {
            log.error("Session save failed: {}", e.getMessage());
        }
    }
}
package com.example.abtest.auth; /**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:51:58
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:45:59
 * @FilePath: src/main/java/com/example/abtest/auth/V2Auth.java
 * @Description:
 */
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.Map;

@Component
@Slf4j
public class V2Auth {
    private final String accessKey;
    private final String secretKey;

    public V2Auth(
            @Value("${abtest.v2.access-key}") String accessKey,
            @Value("${abtest.v2.secret-key}") String secretKey) {
        this.accessKey = accessKey;
        this.secretKey = secretKey;
    }

    public Map<String, String> getHeaders() {
        long timestamp = System.currentTimeMillis() / 1000;
        return Map.of(
                "X-Access-Key", accessKey,
                "X-Timestamp", String.valueOf(timestamp),
                "X-Signature", generateSignature(timestamp)
        );
    }

    private String generateSignature(long timestamp) {
        try {
            Mac hmac = Mac.getInstance("HmacSHA256");
            hmac.init(new SecretKeySpec(secretKey.getBytes(), "HmacSHA256"));
            byte[] hash = hmac.doFinal(
                    (timestamp + "\n" + accessKey).getBytes()
            );
            return Hex.encodeHexString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Signature error", e);
        }
    }
}

/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:08:12
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:25:50
 * @FilePath: src/main/java/com/example/abtest/client/ExperimentClient.java
 * @Description:
 */
package com.example.abtest.client;

public interface ExperimentClient {
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:25:50
 * @FilePath: src/main/java/com/example/abtest/client/V1Client.java
 * @Description:
 */
// src/main/java/com/example/abtest/service/client/V1Client.java
package com.example.abtest.client;

import com.example.abtest.auth.V1Auth;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class V1Client implements Client {

    private final RestTemplate restTemplate;
    private final V1Auth authProvider;
    private final String baseUrl;

    public V1Client(RestTemplate restTemplate,
                    V1Auth authProvider,
                    AppProperties appProperties) {
        this.restTemplate = restTemplate;
        this.authProvider = authProvider;
        this.baseUrl = appProperties.getV1BaseUrl();
    }

    @Override
    public Object getExperimentDetails(Integer appId, Integer experimentId, Map<String, Object> params) {
        HttpHeaders headers = new HttpHeaders();
        headers.addAll(authProvider.getAuthHeaders());
        headers.setContentType(MediaType.APPLICATION_JSON);

        String url = baseUrl + "/datatester/api/v2/flight/view?flight_id={flightId}&is_duplicate={isDuplicate}";
        return restTemplate.exchange(
                url,
                HttpMethod.GET,
                new HttpEntity<>(headers),
                Object.class,
                params.get("flight_id"),
                params.get("is_duplicate")
        ).getBody();
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:08:22
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:41:43
 * @FilePath: src/main/java/com/example/abtest/client/V2Client.java
 * @Description:
 */
package com.example.abtest.client;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class V2Client implements ExperimentClient {
    private final RestTemplate restTemplate;
    private final V2Auth authProvider;
    private final String baseUrl;

    public V2Client(RestTemplate restTemplate,
                    V2Auth authProvider,
                    @Value("${abtest.v2.base-url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.authProvider = authProvider;
        this.baseUrl = baseUrl;
    }

    @Override
    public Map<String, Object> getDetails(Map<String, Object> params) {
        HttpHeaders headers = new HttpHeaders();
        headers.addAll(authProvider.getHeaders());

        String url = baseUrl + "/openapi/v2/apps/{appId}/experiments/{experimentId}/details";
        return restTemplate.exchange(
                url,
                HttpMethod.GET,
                new HttpEntity<>(headers),
                Map.class,
                params.get("app_id"),
                params.get("experiment_id")
        ).getBody();
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 11:01:48
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:25:50
 * @FilePath: src/main/java/com/example/abtest/config/ABTestConfig.java
 * @Description:
 */
package com.example.abtest.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.NestedConfigurationProperty;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.annotation.Validated;

@Configuration
@ConfigurationProperties(prefix = "abtest")
@Validated
public class ABTestConfig {
    @NestedConfigurationProperty
    private V1Config v1;

    @NestedConfigurationProperty
    private V2Config v2;

    @Data
    public static class V1Config {
        @NotEmpty
        private String baseUrl;
        private String sessionFile;
    }

    @Data
    public static class V2Config {
        @NotEmpty
        private String baseUrl;
        private String accessKey;
        private String secretKey;
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 11:10:39
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:42:02
 * @FilePath: src/main/java/com/example/abtest/config/RestTemplateConfig.java
 * @Description:
 */
package com.example.abtest.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

@Configuration
public class RestTemplateConfig {
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(10))
                .setReadTimeout(Duration.ofSeconds(30))
                .build();
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:42:55
 * @FilePath: src/main/java/com/example/abtest/controller/ABTestController.java
 * @Description:
 */
package com.example.abtest.controller;

import com.example.abtest.model.ResponseResult;
import com.example.abtest.service.ABTestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

// src/main/java/com/example/abtest/controller/ABTestController.java
@RestController
@RequestMapping("/openapi")
public class ABTestController {
    private final ABTestService abTestService;

    @Autowired
    public ABTestController(ABTestService abTestService) {
        this.abTestService = abTestService;
    }

    @GetMapping("/v{version}/apps/{appId}/experiment/{experimentId}/details")
    public ResponseResult getExperimentDetails(
            @PathVariable String version,
            @PathVariable Long appId,
            @PathVariable Long experimentId) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version);
        params.put("app_id", appId);
        params.put("experiment_id", experimentId);

        return abTestService.getExperimentDetails(params);
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:25:50
 * @FilePath: src/main/java/com/example/abtest/exception/GlobalExceptionHandler.java
 * @Description:
 */
package com.example.abtest.exception;

import com.example.abtest.model.ResponseResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.context.request.WebRequest;

import java.util.List;
import java.util.stream.Collectors;

// src/main/java/com/example/abtest/exception/GlobalExceptionHandler.java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ResponseResult> handleException(Exception ex, WebRequest request) {
        log.error("Global exception: {} - Request: {}", ex.getMessage(), request.getDescription(false), ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ResponseResult.error(500, "系统繁忙，请稍后重试"));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ResponseResult> handleValidationExceptions(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.toList());

        return ResponseEntity.badRequest()
                .body(ResponseResult.error(400, "参数校验失败: " + String.join(", ", errors)));
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:45:59
 * @FilePath: src/main/java/com/example/abtest/model/ResponseResult.java
 * @Description:
 */
package com.example.abtest.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

// src/main/java/com/example/abtest/model/ApiResponse.java
// ResponseResult.java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ResponseResult {
    private int code;
    private String message;
    private Object data;

    public static ResponseResult success(Object data) {
        return new ResponseResult(200, "success", data);
    }

    public static ResponseResult error(int code, String message) {
        return new ResponseResult(code, message, null);
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:42:27
 * @FilePath: src/main/java/com/example/abtest/service/ABTestService.java
 * @Description:
 */
package com.example.abtest.service;

import com.example.abtest.adapter.ExperimentAdapter;
import com.example.abtest.client.ExperimentClient;
import com.example.abtest.model.ResponseResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

// ABTestService.java
@Service
public class ABTestService {
    private final Map<String, ExperimentAdapter> adapters;
    private final Map<String, ExperimentClient> clients;

    @Autowired
    public ABTestService(Map<String, ExperimentAdapter> adapters,
                         Map<String, ExperimentClient> clients) {
        this.adapters = adapters;
        this.clients = clients;
    }

    public ResponseResult getExperimentDetails(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toUpperCase();
            if (!adapters.containsKey(version) || !clients.containsKey(version)) {
                return ResponseResult.error(400, "不支持的版本类型");
            }

            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertGetDetailsRequest(params);
            Map<String, Object> response = client.getDetails(convertedParams);
            return ResponseResult.success(adapter.convertGetDetailsResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "服务处理异常");
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 15:33:20
 * @FilePath: src/main/java/com/example/abtest/AbtestApplication.java
 * @Description:
 */
// src/main/java/com/example/abtest/ABTestApplication.java
package com.example.abtest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class AbtestApplication {
    public static void main(String[] args) {
        SpringApplication.run(AbtestApplication.class, args);
    }
}
###
 # @Author: ChZheng
 # @Date: 2025-04-14 14:06:11
 # @LastEditors: ChZheng
 # @LastEditTime: 2025-04-15 15:49:50
 # @FilePath: src/main/resources/application.yml
 # @Description:
###
# application.yml 改造为环境变量注入
spring:
  profiles:
    active: @activated.properties@  # Maven过滤占位符

abtest:
  env: ${ABTEST_ENV:local}  # 环境标识
  v1:
    base-url: ${V1_BASE_URL:http://localhost:8081}
    session-file: ${V1_SESSION_FILE:./session.txt}  # 本地开发路径
    login-url: ${V1_LOGIN_URL:/api/login}
  v2:
    base-url: ${V2_BASE_URL:http://localhost:8082}
    access-key: ${V2_ACCESS_KEY:default_key}
    secret-key: ${V2_SECRET_KEY:default_secret}

management:
  endpoints:
    web:
      exposure:
        include: health,info
###
 # @Author: ChZheng
 # @Date: 2025-04-15 15:49:27
 # @LastEditors: ChZheng
 # @LastEditTime: 2025-04-15 15:54:37
 # @FilePath: src/main/resources/application-dev.yml
 # @Description:
###

spring:
  config:
    activate:
      on-profile: dev

abtest:
  v1:
    base-url: http://dev-api.example.com
  v2:
    base-url: http://dev-v2-api.example.com

###
 # @Author: ChZheng
 # @Date: 2025-04-15 15:49:27
 # @LastEditors: ChZheng
 # @LastEditTime: 2025-04-15 15:54:37
 # @FilePath: src/main/resources/application-prod.yml
 # @Description:
###

spring:
  config:
    activate:
      on-profile: prod

abtest:
  v1:
    session-file: /data/abtest/session.txt  # K8s持久化路径
    base-url: http://prod-v1-api.example.com
  v2:
    base-url: http://prod-v2-api.example.com

###
 # @Author: ChZheng
 # @Date: 2025-04-15 15:49:27
 # @LastEditors: ChZheng
 # @LastEditTime: 2025-04-15 15:49:29
 # @FilePath: src/main/resources/application-test.yml
 # @Description:
###
