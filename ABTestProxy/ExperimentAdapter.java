/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/ExperimentAdapter.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:07:56
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
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
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/V1Adapter.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
 * @FilePath: src/main/java/com/example/abtest/adapter/V1Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.ExperimentAdapter;
import org.springframework.stereotype.Component;

import java.text.SimpleDateFormat;
import java.util.*;
import java.util.stream.Collectors;

import static java.util.Map.*;

@Component
public class V1Adapter implements ExperimentAdapter {

    // ==== 实验创建 ====
    @Override
    public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
        params.put("hash_strategy", "ssid");
        return params;
    }

    @Override
    public Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response) {
        return response;
    }

    // ==== 实验详情 ====
    @Override
    public Map<String, Object> convertGetDetailsRequest(Map<String, Object> params) {
        params.put("is_duplicate", false);
        return params;
    }

    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        if (!"200".equals(String.valueOf(response.get("code")))) {
            return response;
        }

        Map<String, Object> data = (Map<String, Object>) response.get("data");
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

        Map<String, Object> layer = new HashMap<>();
        Map<String, Object> layerInfo = (Map<String, Object>) data.get("layer_info");
        layer.put("name", layerInfo.get("layer_name"));
        layer.put("status", layerInfo.get("layer_status"));
        layer.put("type", layerInfo.get("type"));
        layer.put("description", "");

        List<Map<String, Object>> versions = ((List<Map<String, Object>>) data.get("versions"))
                .stream()
                .map(v -> Map.of(
                        "id", v.get("id"),
                        "name", v.get("name"),
                        "type", v.get("type"),
                        "config", v.get("config"),
                        "description", v.get("description"),
                        "weight", v.get("weight")
                ))
                .collect(Collectors.toList());

        List<Map<String, Object>> metrics = ((List<Map<String, Object>>) data.get("metrics"))
                .stream()
                .map(m -> {
                    Map<String, Object> metric = ((List<Map<String, Object>>) m.get("metrics")).get(0);
                    return Map.of(
                            "id", metric.get("id"),
                            "name", metric.get("name"),
                            "metric_description", metric.get("description"),
                            "type", metric.get("type")
                    );
                })
                .collect(Collectors.toList());

        return Map.of(
                "code", 200,
                "message", "success",
                "data", Map.ofEntries(
                        entry("id", data.get("id")),
                        entry("name", data.get("flight_name")),
                        entry("start_ts", sdf.format(new Date((Long) data.get("start_time") * 1000))),
                        entry("end_ts", sdf.format(new Date((Long) data.get("end_time") * 1000))),
                        entry("owner", data.get("owner")),
                        entry("description", data.get("description")),
                        entry("status", data.get("status")),
                        entry("type", "client"),
                        entry("mode", data.get("mode")),
                        entry("layer", Map.of(  // 嵌套子结构
                                "name", layerInfo.get("layer_name"),
                                "status", layerInfo.get("layer_status"),
                                "type", layerInfo.get("type"),
                                "description", ""
                        )),
                        entry("version_resource", data.get("version_resource")),
                        entry("versions", versions),
                        entry("metrics", metrics),
                        entry("whitelist", Collections.emptyList())
                )
        );

    }

    // ==== 报告生成 ====
    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        params.put("trace_data", params.getOrDefault("trace_data", ""));
        return params;
    }

    @Override
    public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
        return response;
    }

    // ==== 状态修改 ====
    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return Map.of(
                "flight_id", params.get("experiment_id"),
                "action", params.get("action")
        );
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        return Map.of(
                "code", response.get("code"),
                "message", response.get("message"),
                "data", Map.of("status", ((Map) response.get("data")).get("status"))
        );
    }

    // ==== 指标列表 ====
    @Override
    public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
        return params;
    }

    @Override
    public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
        List<Map<String, Object>> converted = new ArrayList<>();
        for (Map<String, Object> item : (List<Map<String, Object>>) response.get("data")) {
            converted.add(Map.of(
                    "id", item.get("id"),
                    "name", item.get("name"),
                    "description", item.get("description")
            ));
        }
        return Map.of(
                "code", 200,
                "data", converted,
                "message", "success"
        );
    }

    // ==== 互斥组 ====
    @Override
    public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
        params.put("need_default", false);
        return params;
    }

    @Override
    public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
        return response;
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/V2Adapter.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:07:08
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
 * @FilePath: src/main/java/com/example/abtest/adapter/V2Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.ExperimentAdapter;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Component
public class V2Adapter implements ExperimentAdapter {

    // ==== 实验创建 ====
    @Override
    public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }

    // ==== 实验详情 ====
    @Override
    public Map<String, Object> convertGetDetailsRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }

    // ==== 报告生成 ====
    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }

    // ==== 状态修改 ====
    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }

    // ==== 指标列表 ====
    @Override
    public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }

    // ==== 互斥组 ====
    @Override
    public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
        return new HashMap<>(params); // 参数透传
    }

    @Override
    public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
        return response; // 直接返回原始响应
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:25
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/auth/V1Auth.java
 */
package com.example.abtest.auth;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.Map;

@Slf4j
@Component
public class V1Auth {
    private String sessionId;
    private final String sessionFile;
    private final String loginUrl;
    private final String targetUrl;
    private final String username;
    private final String password;
    private final RestTemplate restTemplate;

    public V1Auth(
            @Value("${abtest.v1.session-file}") String sessionFile,
            @Value("${abtest.v1.login-url}") String loginUrl,
            @Value("${abtest.v1.target-url}") String targetUrl,
            @Value("${abtest.v1.username}") String username,
            @Value("${abtest.v1.password}") String password,
            RestTemplateBuilder restTemplateBuilder) {

        this.sessionFile = sessionFile;
        this.loginUrl = loginUrl;
        this.targetUrl = targetUrl;
        this.username = username;
        this.password = password;
        this.restTemplate = restTemplateBuilder
                .setConnectTimeout(java.time.Duration.ofSeconds(10))
                .build();
        loadSession();
    }

    public HttpHeaders getHeaders() {
        if (sessionId == null || !validateSession()) {
            refreshSession();
        }
        HttpHeaders headers = new HttpHeaders();
        headers.add("Cookie", "sessionid=" + sessionId);
        return headers;
    }

    private void loadSession() {
        try {
            if (Files.exists(Paths.get(sessionFile))) {
                sessionId = Files.readString(Paths.get(sessionFile)).trim();
                log.info("Loaded session ID: {}", sessionId);
            }
        } catch (IOException e) {
            log.error("Session load failed: {}", e.getMessage());
        }
    }

    private boolean validateSession() {
        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    targetUrl,
                    HttpMethod.GET,
                    new HttpEntity<>(getHeaders()),
                    String.class
            );
            return response.getStatusCode().is2xxSuccessful();
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
                        try {
                            Files.writeString(Paths.get(sessionFile), sessionId);
                        } catch (IOException e) {
                            log.error("Session save failed: {}", e.getMessage());
                        }
                    });
        } catch (Exception e) {
            log.error("V1 login failed: {}", e.getMessage());
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/auth/V2Auth.java
 */
package com.example.abtest.auth;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.Map;
import org.apache.commons.codec.binary.Hex;

@Slf4j
@Component
public class V2Auth {
    private final String accessKey;
    private final String secretKey;

    public V2Auth(
            @Value("${abtest.v2.access-key}") String accessKey,
            @Value("${abtest.v2.secret-key}") String secretKey) {
        this.accessKey = accessKey;
        this.secretKey = secretKey;
    }

    public HttpHeaders getHeaders() {
        long timestamp = System.currentTimeMillis() / 1000;
        return new HttpHeaders() {{
            add("X-Access-Key", accessKey);
            add("X-Timestamp", String.valueOf(timestamp));
            add("X-Signature", generateSignature(timestamp));
        }};
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
            log.error("Signature generation failed: {}", e.getMessage());
            return "";
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/ExperimentClient.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:08:12
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
 * @FilePath: src/main/java/com/example/abtest/client/ExperimentClient.java
 * @Description:
 */
package com.example.abtest.client;

import java.util.Map;

// ExperimentClient.java
public interface ExperimentClient {
    Map<String, Object> createExperiment(Map<String, Object> params);
    Map<String, Object> getDetails(Map<String, Object> params);
    Map<String, Object> generateReport(Map<String, Object> params);
    Map<String, Object> modifyStatus(Map<String, Object> params);
    Map<String, Object> listMetrics(Map<String, Object> params);
    Map<String, Object> listGroups(Map<String, Object> params);

    default Map<String, Object> notImplemented() {
        throw new UnsupportedOperationException("方法未实现");
    }
}

/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/V1Client.java
 */
package com.example.abtest.client;

import com.example.abtest.auth.V1Auth;
import com.example.abtest.client.ExperimentClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
public class V1Client implements ExperimentClient {
    private final RestTemplate restTemplate;
    private final V1Auth authProvider;
    private final String baseUrl;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public V1Client(RestTemplate restTemplate,
                    V1Auth authProvider,
                    @Value("${abtest.v1.base-url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.authProvider = authProvider;
        this.baseUrl = baseUrl;
    }

    // 1. 创建实验

    @Override
    public Map<String, Object> createExperiment(Map<String, Object> params) {
        try {
            // Step 1: 初始化草稿
            Map<String, Object> step1Payload = Map.of(
                    "flight_name", params.get("name"),
                    "duration", params.get("duration"),
                    "hash_strategy", params.get("hash_strategy"),
                    "app", params.get("app_id"),
                    "expiration_remind", true,
                    "longrun_remind", true,
                    "report_mode", 0,
                    "mode", 1
            );

            Map<String, Object> step1Res = restTemplate.postForObject(
                    baseUrl + "/api/step1",
                    new HttpEntity<>(step1Payload, authProvider.getHeaders()),
                    Map.class
            );

            String draftId = ((Map<String, String>) step1Res.get("data")).get("draft_id");

            // Step 2: 配置指标
            restTemplate.postForObject(
                    baseUrl + "/api/step2",
                    new HttpEntity<>(Map.of(
                            "major_metric", "1545",
                            "metrics", "1545",
                            "app", params.get("app_id"),
                            "draft_id", draftId
                    ), authProvider.getHeaders()),
                    Map.class
            );

            // Step 3: 配置版本
            List<Map<String, Object>> versions = (List<Map<String, Object>>) params.get("versions");
            String versionsJson = new ObjectMapper().writeValueAsString(
                    versions.stream().map(v -> Map.of(
                            "type", v.get("type"),
                            "id", v.get("id"),
                            "name", v.get("name"),
                            "lable", v.get("label"),
                            "users", v.getOrDefault("users", Collections.emptyList()),
                            "weight", v.getOrDefault("weight", 50),
                            "config", v.get("config")
                    )).collect(Collectors.toList())
            );

            restTemplate.postForObject(
                    baseUrl + "/api/step3",
                    new HttpEntity<>(Map.of(
                            "versions", versionsJson,
                            "app", params.get("app_id"),
                            "draft_id", draftId
                    ), authProvider.getHeaders()),
                    Map.class
            );

            // Step 4: 提交实验
            Map<String, Object> layerInfo = (Map<String, Object>) params.get("layer_info");
            String layerInfoJson = new ObjectMapper().writeValueAsString(layerInfo);

            return restTemplate.postForObject(
                    baseUrl + "/api/step4",
                    new HttpEntity<>(Map.of(
                            "skip_verification", false,
                            "is_start", true,
                            "distribute", true,
                            "versions", versionsJson,
                            "filter_rule", "[]",
                            "layer_info", layerInfoJson,
                            "app", params.get("app_id"),
                            "draft_id", draftId,
                            "version_freeze_status", 0
                    ), authProvider.getHeaders()),
                    Map.class
            );
        } catch (Exception e) {
            return Map.of("code", 500, "message", e.getMessage());
        }
    }


    // 2. 获取实验详情
    @Override
    public Map<String, Object> getDetails(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.add("flight_id", params.get("flight_id").toString());
        queryParams.add("is_duplicate", params.get("is_duplicate").toString());

        return restTemplate.exchange(
                baseUrl + "/datatester/api/v2/flight/view",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                queryParams
        ).getBody();
    }

    // 3. 生成报告
    @Override
    public Map<String, Object> generateReport(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.add("report_type", params.get("report_type").toString());
        queryParams.add("start_ts", params.get("start_ts").toString());
        queryParams.add("end_ts", params.get("end_ts").toString());
        queryParams.add("trace_data", params.get("trace_data").toString());

        return restTemplate.exchange(
                baseUrl + "/datatester/api/v2/app/{app_id}/flight/{flight_id}/rich-metric-report",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of(
                        "app_id", params.get("app_id"),
                        "flight_id", params.get("flight_id")
                ),
                queryParams
        ).getBody();
    }

    // 4. 修改实验状态
    @Override
    public Map<String, Object> modifyStatus(Map<String, Object> params) {
        String action = params.get("action").toString();
        if (!List.of("launch", "stop").contains(action)) {
            return Map.of("code", 400, "message", "无效操作类型");
        }

        return restTemplate.exchange(
                baseUrl + "/datatester/api/v2/flight/" + action,
                HttpMethod.PUT,
                new HttpEntity<>(Map.of("flight_id", params.get("flight_id")), authProvider.getHeaders()),
                Map.class
        ).getBody();
    }

    // 5. 获取指标列表
    @Override
    public Map<String, Object> listMetrics(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        addParam(queryParams, "keyword", params.get("keyword"));
        addParam(queryParams, "status", params.get("status"));
        addParam(queryParams, "is_required", params.get("is_required"));
        addParam(queryParams, "need_page", params.get("need_page"));
        addParam(queryParams, "page_size", params.get("page_size"));

        return restTemplate.exchange(
                baseUrl + "/datatester/api/v2/app/{app_id}/metric/list",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of("app_id", params.get("app_id")),
                queryParams
        ).getBody();
    }

    // 6. 获取互斥组
    @Override
    public Map<String, Object> listGroups(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        addParam(queryParams, "keyword", params.get("keyword"));
        addParam(queryParams, "status", params.get("status"));
        addParam(queryParams, "need_page", params.get("need_page"));
        addParam(queryParams, "page_size", params.get("page_size"));
        addParam(queryParams, "page", params.get("page"));
        addParam(queryParams, "need_default", params.get("need_default"));

        return restTemplate.exchange(
                baseUrl + "/datatester/api/v2/app/{app_id}/layer/list",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of("app_id", params.get("app_id")),
                queryParams
        ).getBody();
    }

    private void addParam(MultiValueMap<String, String> params, String key, Object value) {
        if (value != null) {
            params.add(key, value.toString());
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/V2Client.java
 */
package com.example.abtest.client;

import com.example.abtest.auth.V2Auth;
import com.example.abtest.client.ExperimentClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

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

    // 1. 创建实验
    @Override
    public Map<String, Object> createExperiment(Map<String, Object> params) {
        List<Map<String, Object>> versions = convertVersions((List<?>) params.get("versions"));

        return restTemplate.postForObject(
                baseUrl + "/openapi/v2/apps/{app_id}/experiments",
                new HttpEntity<>(Map.of(
                        "name", params.get("name"),
                        "mode", params.get("mode"),
                        "endpoint_type", params.get("endpoint_type"),
                        "duration", params.get("duration"),
                        "major_metric", params.get("major_metric"),
                        "metrics", params.get("metrics"),
                        "versions", versions,
                        "layer_info", params.getOrDefault("layer_info", Map.of("layer_id", -1))
                ), authProvider.getHeaders()),
                Map.class,
                params.get("app_id")
        );
    }

    // 2. 获取实验详情
    @Override
    public Map<String, Object> getDetails(Map<String, Object> params) {
        return restTemplate.exchange(
                baseUrl + "/openapi/v2/apps/{app_id}/experiments/{experiment_id}/details",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of(
                        "app_id", params.get("app_id"),
                        "experiment_id", params.get("experiment_id")
                )
        ).getBody();
    }

    // 3. 生成报告
    @Override
    public Map<String, Object> generateReport(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.add("report_type", params.get("report_type").toString());
        queryParams.add("start_ts", params.get("start_ts").toString());
        queryParams.add("end_ts", params.get("end_ts").toString());
        queryParams.add("filters", params.getOrDefault("filters", "").toString());

        return restTemplate.exchange(
                baseUrl + "/openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of(
                        "app_id", params.get("app_id"),
                        "experiment_id", params.get("experiment_id")
                ),
                queryParams
        ).getBody();
    }

    // 4. 修改实验状态
    @Override
    public Map<String, Object> modifyStatus(Map<String, Object> params) {
        String action = params.get("action").toString();
        if (!List.of("launch", "stop").contains(action)) {
            return Map.of("code", 400, "message", "无效操作类型");
        }

        return restTemplate.exchange(
                baseUrl + "/openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}",
                HttpMethod.PUT,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of(
                        "app_id", params.get("app_id"),
                        "experiment_id", params.get("experiment_id"),
                        "action", action
                )
        ).getBody();
    }

    // 5. 获取指标列表
    @Override
    public Map<String, Object> listMetrics(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        addParam(queryParams, "keyword", params.get("keyword"));
        addParam(queryParams, "page", params.get("page"));
        addParam(queryParams, "page_size", params.get("page_size"));

        return restTemplate.exchange(
                baseUrl + "/openapi/v2/apps/{app_id}/metrics",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of("app_id", params.get("app_id")),
                queryParams
        ).getBody();
    }

    // 6. 获取互斥组
    @Override
    public Map<String, Object> listGroups(Map<String, Object> params) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        addParam(queryParams, "need_page", params.get("need_page"));
        addParam(queryParams, "page", params.get("page"));
        addParam(queryParams, "page_size", params.get("page_size"));

        return restTemplate.exchange(
                baseUrl + "/openapi/v2/apps/{app_id}/layers",
                HttpMethod.GET,
                new HttpEntity<>(authProvider.getHeaders()),
                Map.class,
                Map.of("app_id", params.get("app_id")),
                queryParams
        ).getBody();
    }

    private List<Map<String, Object>> convertVersions(List<?> versions) {
        return versions.stream()
                .map(v -> (Map<String, Object>) v)
                .map(v -> Map.of(
                        "type", v.get("type"),
                        "name", v.get("name"),
                        "description", v.getOrDefault("description", ""),
                        "weight", v.getOrDefault("weight", 50),
                        "config", v.get("config"),
                        "users", v.getOrDefault("users", Collections.emptyList())
                )).collect(Collectors.toList());
    }

    private void addParam(MultiValueMap<String, String> params, String key, Object value) {
        if (value != null) {
            params.add(key, value.toString());
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/config/ABTestConfig.java
 */
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.NestedConfigurationProperty;
import org.springframework.context.annotation.Configuration;
import org.springframework.validation.annotation.Validated;

@Configuration
@ConfigurationProperties(prefix = "abtest")
@Validated
@Data
public class ABTestConfig {
    // 新增版本控制字段
    private String activeVersion = "v1"; // 默认版本

    // 新增环境判断方法
    public boolean isLocal() {
        return "dev".equals(env);
    }

    // 原字段保持不变
    private String env;
    @NestedConfigurationProperty
    private V1Config v1;
    @NestedConfigurationProperty
    private V2Config v2;

    @Data
    public static class V1Config {
        @NotEmpty
        private String baseUrl;
        private String sessionFile;
        // 补充Python中的配置项
        private String loginUrl;
        private String targetUrl;
        private String username;
        private String password;
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
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/config/RestTemplateConfig.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 11:10:39
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
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
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/controller/ABTestController.java
 */
package com.example.abtest.controller;

import com.example.abtest.model.ResponseResult;
import com.example.abtest.service.ABTestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/openapi")
public class ABTestController {
    private final ABTestService abTestService;

    @Autowired
    public ABTestController(ABTestService abTestService) {
        this.abTestService = abTestService;
    }

    // 创建实验
    @PostMapping("/{version}/apps/{appId}/experiments")
    public ResponseResult createExperiment(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestBody Map<String, Object> body) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase()); // 统一转小写
        params.put("app_id", appId);
        params.putAll(body);

        return abTestService.createExperiment(params);
    }

    // 获取实验详情
    @GetMapping("/{version}/apps/{appId}/experiment/{experimentId}/details")
    public ResponseResult getExperimentDetails(
            @PathVariable String version,
            @PathVariable Long appId,
            @PathVariable Long experimentId) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase());
        params.put("app_id", appId);
        params.put("experiment_id", experimentId);

        return abTestService.getExperimentDetails(params);
    }

    // 生成实验报告
    @GetMapping("/{version}/apps/{appId}/experiment/{experimentId}/metrics")
    public ResponseResult generateReport(
            @PathVariable String version,
            @PathVariable Long appId,
            @PathVariable Long experimentId,
            @RequestParam String reportType,
            @RequestParam String startTs,
            @RequestParam String endTs,
            @RequestParam(required = false) String filters) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase());
        params.put("app_id", appId);
        params.put("experiment_id", experimentId);
        params.put("report_type", reportType);
        params.put("start_ts", startTs);
        params.put("end_ts", endTs);
        params.put("filters", filters);

        return abTestService.generateReport(params);
    }

    // 修改实验状态
    @PutMapping("/{version}/apps/{appId}/experiments/{experimentId}/{action}")
    public ResponseResult modifyExperimentStatus(
            @PathVariable String version,
            @PathVariable Long appId,
            @PathVariable Long experimentId,
            @PathVariable String action) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase());
        params.put("app_id", appId);
        params.put("experiment_id", experimentId);
        params.put("action", action.toLowerCase()); // 统一转小写

        return abTestService.modifyExperimentStatus(params);
    }

    // 获取指标列表
    @GetMapping("/{version}/apps/{appId}/metrics")
    public ResponseResult listMetrics(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(defaultValue = "1") int needPage) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase());
        params.put("app_id", appId);
        params.put("keyword", keyword);
        params.put("page", page);
        params.put("page_size", pageSize);
        params.put("need_page", needPage);

        return abTestService.listAvailableMetrics(params);
    }

    // 获取互斥组列表
    @GetMapping("/{version}/apps/{appId}/layers")
    public ResponseResult listMutexGroups(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(defaultValue = "1") int needPage) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version.toLowerCase());
        params.put("app_id", appId);
        params.put("keyword", keyword);
        params.put("page", page);
        params.put("page_size", pageSize);
        params.put("need_page", needPage);

        return abTestService.listMutexGroups(params);
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 07:00:41
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/model/ResponseResult.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
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
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/service/ABTestService.java
 */
package com.example.abtest.service;

import com.example.abtest.adapter.ExperimentAdapter;
import com.example.abtest.client.ExperimentClient;
import com.example.abtest.model.ResponseResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Map;

@Slf4j
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

    // 统一版本校验方法
    private void validateVersion(String version) {
        if (!adapters.containsKey(version) || !clients.containsKey(version)) {
            log.error("不支持的版本: {}", version);
            throw new IllegalArgumentException("Unsupported version: " + version);
        }
    }

    // 统一服务执行模板
    private ResponseResult executeServiceCall(
            Map<String, Object> params,
            String operationName,
            ServiceFunction function
    ) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            validateVersion(version);

            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            return function.apply(adapter, client);

        } catch (IllegalArgumentException e) {
            log.warn("参数校验失败: {}", e.getMessage());
            return ResponseResult.error(400, e.getMessage());
        } catch (Exception e) {
            log.error("{} 服务异常: {}", operationName, e.getMessage(), e);
            return ResponseResult.error(500, operationName + "失败");
        }
    }

    // 创建实验
    public ResponseResult createExperiment(Map<String, Object> params) {
        return executeServiceCall(params, "实验创建", (adapter, client) -> {
            Map<String, Object> convertedParams = adapter.convertCreateExperimentRequest(params);
            Map<String, Object> response = client.createExperiment(convertedParams);
            return ResponseResult.success(adapter.convertCreateExperimentResponse(response));
        });
    }

    // 获取实验详情
    public ResponseResult getExperimentDetails(Map<String, Object> params) {
        return executeServiceCall(params, "详情查询", (adapter, client) -> {
            Map<String, Object> convertedParams = adapter.convertGetDetailsRequest(params);
            Map<String, Object> response = client.getDetails(convertedParams);
            return ResponseResult.success(adapter.convertGetDetailsResponse(response));
        });
    }

    // 生成报告
    public ResponseResult generateReport(Map<String, Object> params) {
        return executeServiceCall(params, "报告生成", (adapter, client) -> {
            Map<String, Object> convertedParams = adapter.convertGenerateReportRequest(params);
            Map<String, Object> response = client.generateReport(convertedParams);
            return ResponseResult.success(adapter.convertGenerateReportResponse(response));
        });
    }

    // 修改状态
    public ResponseResult modifyExperimentStatus(Map<String, Object> params) {
        return executeServiceCall(params, "状态修改", (adapter, client) -> {
            String action = (String) params.get("action");
            if (!Arrays.asList("launch", "stop").contains(action.toLowerCase())) {
                throw new IllegalArgumentException("无效操作类型: " + action);
            }

            Map<String, Object> convertedParams = adapter.convertModifyStatusRequest(params);
            Map<String, Object> response = client.modifyStatus(convertedParams);
            return ResponseResult.success(adapter.convertModifyStatusResponse(response));
        });
    }

    // 查询指标
    public ResponseResult listAvailableMetrics(Map<String, Object> params) {
        return executeServiceCall(params, "指标查询", (adapter, client) -> {
            Map<String, Object> convertedParams = adapter.convertListMetricsRequest(params);
            Map<String, Object> response = client.listMetrics(convertedParams);
            return ResponseResult.success(adapter.convertListMetricsResponse(response));
        });
    }

    // 查询互斥组
    public ResponseResult listMutexGroups(Map<String, Object> params) {
        return executeServiceCall(params, "互斥组查询", (adapter, client) -> {
            Map<String, Object> convertedParams = adapter.convertListGroupsRequest(params);
            Map<String, Object> response = client.listGroups(convertedParams);
            return ResponseResult.success(adapter.convertListGroupsResponse(response));
        });
    }

    // 函数式接口封装
    @FunctionalInterface
    private interface ServiceFunction {
        ResponseResult apply(ExperimentAdapter adapter, ExperimentClient client) throws Exception;
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/util/HttpHelper.java
 */
package com.example.abtest.util;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

// src/main/java/com/example/abtest/util/HttpHelper.java
public class HttpHelper {
    private static final RestTemplate restTemplate = new RestTemplate();

    public static Map<String, Object> fetchData(String url,
                                                Map<String, Object> params,
                                                HttpHeaders headers) {
        return executeRequest("GET", url, params, null, headers);
    }

    public static Map<String, Object> postData(String url,
                                               Map<String, Object> body,
                                               HttpHeaders headers) {
        return executeRequest("POST", url, null, body, headers);
    }

    private static Map<String, Object> executeRequest(String method,
                                                      String url,
                                                      Map<String, Object> params,
                                                      Map<String, Object> body,
                                                      HttpHeaders headers) {
        try {
            MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
            if (params != null) {
                params.forEach((k, v) -> queryParams.add(k, v.toString()));
            }

            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.valueOf(method),
                    new HttpEntity<>(body, headers),
                    Map.class,
                    queryParams
            );

            return response.getBody();
        } catch (HttpStatusCodeException e) {
            return Map.of("code", e.getStatusCode().value(), "message", e.getStatusText());
        } catch (Exception e) {
            return Map.of("code", 500, "message", e.getMessage());
        }
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 05:49:07
 * @LastEditTime: 2025-04-17 07:20:39
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/AbtestApplication.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-17 07:20:39
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
 # @Date: 2025-04-17 05:49:07
 # @LastEditTime: 2025-04-17 07:20:39
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: src/main/resources/application.yml
###
# 所有环境的公共配置
spring:
  profiles:
    active: test

abtest:
  env: ${SPRING_PROFILES_ACTIVE:test}  # 环境标识
  active-version: v1                  # 全局版本控制

  # V1默认配置（所有环境共用）
  v1:
    base-url: ${V1_BASE_URL:http://default-v1.example.com}
    session-file: ${V1_SESSION_FILE:/tmp/session.txt}
    login-url: ${V1_LOGIN_URL:http://default-v1.login}
    target-url: ${V1_TARGET_URL:http://default-v1.target}
    username: ${V1_USERNAME:default_user}
    password: ${V1_PASSWORD:default_pass}

  # V2默认配置（所有环境共用）
  v2:
    base-url: ${V2_BASE_URL:http://default-v2.example.com}
    access-key: ${V2_ACCESS_KEY:default_ak}
    secret-key: ${V2_SECRET_KEY:default_sk}

    ###
 # @Author: ChZheng
 # @Date: 2025-04-17 05:49:07
 # @LastEditTime: 2025-04-17 07:20:39
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: src/main/resources/application-prod.yml
###
spring:
  config:
    activate:
      on-profile: prod

# 仅包含生产环境特有配置
abtest:
  active-version: v2
  v1:
    base-url: ${V1_BASE_URL}
    session-file: /data/abtest/session.txt
  v2:
    base-url: ${V2_BASE_URL}

###
 # @Author: ChZheng
 # @Date: 2025-04-17 05:49:07
 # @LastEditTime: 2025-04-17 07:20:39
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: src/main/resources/application-test.yml
###
spring:
  config:
    activate:
      on-profile: test

abtest:
  active-version: v2
  # V1默认配置（所有环境共用）
  v1:
    base-url: ${V1_BASE_URL:http://default-v1.example.com}
    session-file: ${V1_SESSION_FILE:/tmp/session.txt}
    login-url: ${V1_LOGIN_URL:http://default-v1.login}
    target-url: ${V1_TARGET_URL:http://default-v1.target}
    username: ${V1_USERNAME:default_user}
    password: ${V1_PASSWORD:default_pass}

  # V2默认配置（所有环境共用）
  v2:
    base-url: ${V2_BASE_URL:http://default-v2.example.com}
    access-key: ${V2_ACCESS_KEY:default_ak}
    secret-key: ${V2_SECRET_KEY:default_sk}

