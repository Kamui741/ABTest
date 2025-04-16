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
 * @LastEditTime: 2025-04-16 10:18:29
 * @FilePath: src/main/java/com/example/abtest/adapter/V1Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.ExperimentAdapter;
import org.springframework.stereotype.Component;

import java.text.SimpleDateFormat;
import java.util.*;


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
    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        if (!"200".equals(String.valueOf(response.get("code")))) {
            return response;
        }

        Map<String, Object> data = (Map<String, Object>) response.get("data");
        Map<String, Object> converted = new LinkedHashMap<>();

        // 时间格式转换
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        converted.put("start_ts", sdf.format(new Date((Long)data.get("start_time") * 1000)));
        converted.put("end_ts", sdf.format(new Date((Long)data.get("end_time") * 1000)));

        // 层级信息转换
        Map<String, Object> layerInfo = (Map<String, Object>) data.get("layer_info");
        Map<String, Object> layer = new HashMap<>();
        layer.put("name", layerInfo.get("layer_name"));
        layer.put("status", layerInfo.get("layer_status"));
        layer.put("type", layerInfo.get("type"));

        // 版本信息转换
        List<Map<String, Object>> versions = new ArrayList<>();
        for (Map<String, Object> v : (List<Map<String, Object>>) data.get("versions")) {
            Map<String, Object> version = new HashMap<>();
            version.put("id", v.get("id"));
            version.put("name", v.get("name"));
            version.put("type", v.get("type"));
            version.put("config", v.get("config"));
            version.put("description", v.get("description"));
            version.put("weight", v.get("weight"));
            versions.add(version);
        }

        // 指标信息转换
        List<Map<String, Object>> metrics = new ArrayList<>();
        for (Map<String, Object> m : (List<Map<String, Object>>) data.get("metrics")) {
            Map<String, Object> metric = new HashMap<>();
            Map<String, Object> metricData = ((List<Map<String, Object>>) m.get("metrics")).get(0);
            metric.put("id", metricData.get("id"));
            metric.put("name", metricData.get("name"));
            metric.put("metric_description", metricData.get("description"));
            metric.put("type", metricData.get("type"));
            metrics.add(metric);
        }

        // 构建最终响应
        Map<String, Object> result = new HashMap<>();
        result.put("code", 200);
        result.put("message", "success");
        result.put("data", Map.of(
                "id", data.get("id"),
                "name", data.get("flight_name"),
                "owner", data.get("owner"),
                "description", data.get("description"),
                "status", data.get("status"),
                "type", "client",
                "mode", data.get("mode"),
                "layer", layer,
                "version_resource", data.get("version_resource"),
                "versions", versions,
                "metrics", metrics,
                "whitelist", Collections.emptyList()
        ));

        return result;
    }

    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
        // 保持Python结构直接返回
        return response;
    }

    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        return Map.of(
                "code", response.get("code"),
                "message", response.get("message"),
                "data", Map.of("status", response.get("status"))
        );
    }

    @Override
    public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
        List<Map<String, Object>> converted = new ArrayList<>();
        for (Map<String, Object> item : (List<Map<String, Object>>) response.get("data")) {
            Map<String, Object> metric = new HashMap<>();
            metric.put("id", item.get("id"));
            metric.put("name", item.get("name"));
            metric.put("description", item.get("description"));
            converted.add(metric);
        }
        return Map.of(
                "code", 200,
                "data", converted,
                "message", "success"
        );
    }

    @Override
    public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
        return Collections.emptyMap();
    }

    @Override
    public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
        return Collections.emptyMap();
    }
    @Override
    public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
        return Map.of(
                "flight_id", params.get("experiment_id"),
                "action", params.get("action")
        );
    }

    @Override
    public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
        // 保持Python的响应结构
        return Map.of(
                "code", response.get("code"),
                "message", response.get("message"),
                "data", Map.of("status", ((Map)response.get("data")).get("status"))
        );
    }
    // 其他转换方法实现...
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:07:08
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-16 09:23:05
 * @FilePath: src/main/java/com/example/abtest/adapter/V2Adapter.java
 * @Description:
 */
package com.example.abtest.adapter;

import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.HashMap;
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
    @Override
    public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
        // V2参数透传
        return new HashMap<>(params);
    }

    @Override
    public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
        // V2直接返回原始响应
        return response;
    }

    // 其他方法保持透传逻辑
    @Override
    public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
        return new HashMap<>(params);
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
 * @LastEditTime: 2025-04-16 09:21:23
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
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-16 09:59:43
 * @FilePath: src/main/java/com/example/abtest/client/V1Client.java
 * @Description:
 */
// src/main/java/com/example/abtest/service/client/V1Client.java
package com.example.abtest.client;

import com.example.abtest.adapter.ExperimentAdapter;
import com.example.abtest.auth.V1Auth;
import com.example.abtest.model.ResponseResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.Map;

@Component
public class V1Client implements ExperimentClient {
    private final RestTemplate restTemplate;
    private final V1Auth authProvider;
    private final String baseUrl;

    public V1Client(RestTemplate restTemplate,
                    V1Auth authProvider,
                    @Value("${abtest.v1.base-url}") String baseUrl) {  // 使用直接注入
        this.restTemplate = restTemplate;
        this.authProvider = authProvider;
        this.baseUrl = baseUrl;
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
    @Override
    private void validateVersion(String version) {
        if (!adapters.containsKey(version) || !clients.containsKey(version)) {
            throw new IllegalArgumentException("Unsupported version: " + version);
        }
    }

    public ResponseResult getExperimentDetails(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            validateVersion(version);

            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertGetDetailsRequest(params);
            Map<String, Object> response = client.getDetails(convertedParams);
            return ResponseResult.success(adapter.convertGetDetailsResponse(response));
        } catch (IllegalArgumentException e) {
            return ResponseResult.error(400, e.getMessage());
        } catch (Exception e) {
            return ResponseResult.error(500, "服务处理异常");
        }
    }


    @Override
    @Override
    public Map<String, Object> modifyStatus(Map<String, Object> params) {
        String action = (String) params.get("action");
        if (!Arrays.asList("launch", "stop").contains(action)) {
            return Map.of("code", 400, "message", "无效操作类型");
        }

        try {
            String url = String.format("%s/datatester/api/v2/flight/%s", baseUrl, action);
            Map<String, Object> payload = Map.of("flight_id", params.get("flight_id"));

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, authProvider.getHeaders());
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.PUT,
                    request,
                    Map.class
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("修改状态失败: {}", e.getMessage());
            return Map.of("code", 500, "message", "状态修改失败");
        }
    }
    @Override
    public Map<String, Object> listMetrics(Map<String, Object> params) {
        try {
            String url = String.format("%s/datatester/api/v2/app/%s/metric/list",
                    baseUrl, params.get("app_id"));

            MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
            queryParams.add("keyword", (String) params.get("keyword"));
            queryParams.add("status", String.valueOf(params.get("status")));
            queryParams.add("is_required", String.valueOf(params.get("is_required")));
            queryParams.add("need_page", String.valueOf(params.get("need_page")));
            queryParams.add("page_size", String.valueOf(params.get("page_size")));

            HttpEntity<?> request = new HttpEntity<>(authProvider.getHeaders());
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    request,
                    Map.class,
                    queryParams
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("获取指标列表失败: {}", e.getMessage());
            return Map.of("code", 500, "message", "指标获取失败");
        }
    }
    @Override
    public Map<String, Object> listGroups(Map<String, Object> params) {
        try {
            String url = String.format("%s/datatester/api/v2/app/%s/layer/list",
                    baseUrl, params.get("app_id"));

            MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
            queryParams.add("keyword", (String) params.get("keyword"));
            queryParams.add("status", String.valueOf(params.get("status")));
            queryParams.add("need_page", String.valueOf(params.get("need_page")));
            queryParams.add("page_size", String.valueOf(params.get("page_size")));
            queryParams.add("page", String.valueOf(params.get("page")));
            queryParams.add("need_default", String.valueOf(params.get("need_default")));

            HttpEntity<?> request = new HttpEntity<>(authProvider.getHeaders());
            ResponseEntity<Map> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    request,
                    Map.class,
                    queryParams
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("获取互斥组失败: {}", e.getMessage());
            return Map.of("code", 500, "message", "互斥组获取失败");
        }
    }


}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 14:08:22
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-16 10:18:46
 * @FilePath: src/main/java/com/example/abtest/client/V2Client.java
 * @Description:
 */
package com.example.abtest.client;

import com.example.abtest.auth.V2Auth;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
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

    @Override
    public Map<String, Object> createExperiment(Map<String, Object> params) {
        String url = String.format("%s/openapi/v2/apps/%s/experiments",
                baseUrl, params.get("app_id"));

        HttpEntity<Map<String, Object>> request = new HttpEntity<>(params, authProvider.getHeaders());
        return restTemplate.postForObject(url, request, Map.class);
    }

    @Override
    public Map<String, Object> listGroups(Map<String, Object> params) {
        String url = String.format("%s/openapi/v2/apps/%s/layers",
                baseUrl, params.get("app_id"));

        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.add("page", String.valueOf(params.get("page")));
        queryParams.add("page_size", String.valueOf(params.get("page_size")));

        HttpEntity<?> request = new HttpEntity<>(authProvider.getHeaders());
        return restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class,
                queryParams
        ).getBody();
    }
    @Override
    public Map<String, Object> generateReport(Map<String, Object> params) {
        String url = String.format("%s/openapi/v2/apps/%s/experiments/%s/metrics",
                baseUrl, params.get("app_id"), params.get("experiment_id"));

        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.add("report_type", (String) params.get("report_type"));
        queryParams.add("start_ts", (String) params.get("start_ts"));
        queryParams.add("end_ts", (String) params.get("end_ts"));
        queryParams.add("filters", (String) params.get("filters"));

        HttpEntity<?> request = new HttpEntity<>(authProvider.getHeaders());
        return restTemplate.exchange(
                url,
                HttpMethod.GET,
                request,
                Map.class,
                queryParams
        ).getBody();
    }

}
/**
 * @Author: ChZheng
 * @Date: 2025-04-15 11:01:48
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-15 16:19:26
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
@Data
public class ABTestConfig {
    private String env;

    public boolean isProduction() {
        return "prod".equals(env);
    }
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
 * @LastEditTime: 2025-04-16 10:12:39
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

    @PostMapping("/{version}/apps/{appId}/experiments")
    public ResponseResult createExperiment(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestBody Map<String, Object> body) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version);
        params.put("app_id", appId);
        params.putAll(body);

        return abTestService.createExperiment(params);
    }

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
        params.put("version", version);
        params.put("app_id", appId);
        params.put("experiment_id", experimentId);
        params.put("report_type", reportType);
        params.put("start_ts", startTs);
        params.put("end_ts", endTs);
        params.put("filters", filters);

        return abTestService.generateReport(params);
    }

    @GetMapping("/{version}/apps/{appId}/metrics")
    public ResponseResult listMetrics(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(defaultValue = "1") int needPage) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version);
        params.put("app_id", appId);
        params.put("keyword", keyword);
        params.put("page", page);
        params.put("page_size", pageSize);
        params.put("need_page", needPage);

        return abTestService.listAvailableMetrics(params);
    }

    @GetMapping("/{version}/apps/{appId}/layers")
    public ResponseResult listMutexGroups(
            @PathVariable String version,
            @PathVariable Long appId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize,
            @RequestParam(defaultValue = "1") int needPage) {

        Map<String, Object> params = new HashMap<>();
        params.put("version", version);
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
 * @LastEditTime: 2025-04-16 10:14:55
 * @FilePath: src/main/java/com/example/abtest/service/ABTestService.java
 * @Description:
 */
package com.example.abtest.service;

import com.example.abtest.adapter.ExperimentAdapter;
import com.example.abtest.client.ExperimentClient;
import com.example.abtest.model.ResponseResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Arrays;
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

    private void validateVersion(String version) {
        if (!adapters.containsKey(version) || !clients.containsKey(version)) {
            throw new IllegalArgumentException("Unsupported version: " + version);
        }
    }
    public ResponseResult createExperiment(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertCreateExperimentRequest(params);
            Map<String, Object> response = client.createExperiment(convertedParams);
            return ResponseResult.success(adapter.convertCreateExperimentResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "实验创建失败");
        }
    }

    public ResponseResult listMutexGroups(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertListGroupsRequest(params);
            Map<String, Object> response = client.listGroups(convertedParams);
            return ResponseResult.success(adapter.convertListGroupsResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "互斥组查询失败");
        }
    }


    public ResponseResult getExperimentDetails(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            validateVersion(version);

            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertGetDetailsRequest(params);
            Map<String, Object> response = client.getDetails(convertedParams);
            return ResponseResult.success(adapter.convertGetDetailsResponse(response));
        } catch (IllegalArgumentException e) {
            return ResponseResult.error(400, e.getMessage());
        } catch (Exception e) {
            return ResponseResult.error(500, "服务处理异常");
        }
    }

    public ResponseResult generateReport(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertGenerateReportRequest(params);
            Map<String, Object> response = client.generateReport(convertedParams);
            return ResponseResult.success(adapter.convertGenerateReportResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "报告生成失败");
        }
    }

    public ResponseResult listMetrics(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertListMetricsRequest(params);
            Map<String, Object> response = client.listMetrics(convertedParams);
            return ResponseResult.success(adapter.convertListMetricsResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "指标查询失败");
        }
    }


    public ResponseResult modifyExperimentStatus(Map<String, Object> params) {
        try {
            String version = ((String) params.get("version")).toLowerCase();
            String action = (String) params.get("action");

            if (!Arrays.asList("launch", "stop").contains(action)) {
                return ResponseResult.error(400, "无效操作类型");
            }

            ExperimentAdapter adapter = adapters.get(version);
            ExperimentClient client = clients.get(version);

            Map<String, Object> convertedParams = adapter.convertModifyStatusRequest(params);
            Map<String, Object> response = client.modifyStatus(convertedParams);
            return ResponseResult.success(adapter.convertModifyStatusResponse(response));
        } catch (Exception e) {
            return ResponseResult.error(500, "状态修改失败");
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
 # @LastEditTime: 2025-04-16 09:23:28
 # @FilePath: src/main/resources/application.yml
 # @Description:
###
# application.yml 改造为环境变量注入
spring:
  profiles:
    active: @activated.properties@  # Maven过滤占位符

abtest:
  api-endpoints:
    v1:
      create: experiment/create
      details: experiment/detail
      report: report/generate
    v2:
      create: openapi/v2/apps/{appId}/experiments
      details: openapi/v2/apps/{appId}/experiments/{experimentId}/details
      report: openapi/v2/apps/{appId}/experiments/{experimentId}/metrics


management:
  endpoints:
    web:
      exposure:
        include: health,info

