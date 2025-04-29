/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 15:59:31
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/ExperimentAdapter.java
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
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 15:59:51
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/V1Adapter.java
 */

 package com.example.abtest.adapter;

 import com.fasterxml.jackson.databind.ObjectMapper;
 import com.fasterxml.jackson.databind.node.ArrayNode;
 import com.fasterxml.jackson.databind.node.ObjectNode;
 import org.springframework.stereotype.Component;

 import java.text.SimpleDateFormat;
 import java.util.*;

 @Component
 public class V1Adapter implements ExperimentAdapter {
     private static final ObjectMapper mapper = new ObjectMapper();

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

         // 构建主数据结构
         ObjectNode dataNode = mapper.createObjectNode()
                 .put("id", (String) data.get("id"))
                 .put("name", (String) data.get("flight_name"))
                 .put("start_ts", sdf.format(new Date((Long) data.get("start_time") * 1000)))
                 .put("end_ts", sdf.format(new Date((Long) data.get("end_time") * 1000)))
                 .put("owner", (String) data.get("owner"))
                 .put("description", (String) data.get("description"))
                 .put("status", (String) data.get("status"))
                 .put("type", "client")
                 .put("mode", (String) data.get("mode"))
                 .put("version_resource", (String) data.get("version_resource"));

         // 构建嵌套层信息
         Map<String, Object> layerInfo = (Map<String, Object>) data.get("layer_info");
         dataNode.set("layer", mapper.createObjectNode()
                 .put("name", (String) layerInfo.get("layer_name"))
                 .put("status", (String) layerInfo.get("layer_status"))
                 .put("type", (String) layerInfo.get("type"))
                 .put("description", "")
         );

         // 构建版本列表
         ArrayNode versionsNode = mapper.createArrayNode();
         ((List<Map<String, Object>>) data.get("versions")).forEach(v -> {
             versionsNode.add(mapper.createObjectNode()
                     .put("id", (String) v.get("id"))
                     .put("name", (String) v.get("name"))
                     .put("type", (String) v.get("type"))
                     .put("config", (String) v.get("config"))
                     .put("description", (String) v.get("description"))
                     .put("weight", (Integer) v.get("weight"))
             );
         });
         dataNode.set("versions", versionsNode);

         // 构建指标列表
         ArrayNode metricsNode = mapper.createArrayNode();
         ((List<Map<String, Object>>) data.get("metrics")).forEach(m -> {
             Map<String, Object> metric = ((List<Map<String, Object>>) m.get("metrics")).get(0);
             metricsNode.add(mapper.createObjectNode()
                     .put("id", (String) metric.get("id"))
                     .put("name", (String) metric.get("name"))
                     .put("metric_description", (String) metric.get("description"))
                     .put("type", (String) metric.get("type"))
             );
         });
         dataNode.set("metrics", metricsNode);
         dataNode.putArray("whitelist");

         // 构建最终响应
         return mapper.convertValue(mapper.createObjectNode()
                 .put("code", 200)
                 .put("message", "success")
                 .set("data", dataNode), Map.class);
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
         return mapper.convertValue(mapper.createObjectNode()
                 .put("flight_id", params.get("experiment_id").toString())
                 .put("action", params.get("action").toString()), Map.class);
     }

     @Override
     public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
         return mapper.convertValue(mapper.createObjectNode()
                 .put("code", response.get("code").toString())
                 .put("message", response.get("message").toString())
                 .set("data", mapper.createObjectNode()
                         .put("status", ((Map<?, ?>) response.get("data")).get("status").toString())
                 ), Map.class);
     }

     // ==== 指标列表 ====
     @Override
     public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
         return params;
     }

     @Override
     public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
         ArrayNode metricsArray = mapper.createArrayNode();
         ((List<Map<String, Object>>) response.get("data")).forEach(item -> {
             metricsArray.add(mapper.createObjectNode()
                     .put("id", item.get("id").toString())
                     .put("name", item.get("name").toString())
                     .put("description", item.get("description").toString())
             );
         });

         return mapper.convertValue(mapper.createObjectNode()
                 .put("code", 200)
                 .put("message", "success")
                 .set("data", metricsArray), Map.class);
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
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 15:59:56
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/adapter/V2Adapter.java
 */

 package com.example.abtest.adapter;

 import com.fasterxml.jackson.databind.ObjectMapper;
 import org.springframework.stereotype.Component;

 import java.util.Collections;
 import java.util.HashMap;
 import java.util.Map;

 @Component
 public class V2Adapter implements ExperimentAdapter {
     // 使用 Java 8 兼容的 ObjectMapper 声明方式
     private static final ObjectMapper mapper = new ObjectMapper();

     // ==== 实验创建 ==== (保持参数透传逻辑)
     @Override
     public Map<String, Object> convertCreateExperimentRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertCreateExperimentResponse(Map<String, Object> response) {
         return deepCopy(response); // 使用安全的深拷贝
     }

     // ==== 实验详情 ==== (保持透传逻辑)
     @Override
     public Map<String, Object> convertGetDetailsRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertGetDetailsResponse(Map<String, Object> response) {
         return deepCopy(response);
     }

     // ==== 报告生成 ==== (保持透传逻辑)
     @Override
     public Map<String, Object> convertGenerateReportRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertGenerateReportResponse(Map<String, Object> response) {
         return deepCopy(response);
     }

     // ==== 状态修改 ==== (保持透传逻辑)
     @Override
     public Map<String, Object> convertModifyStatusRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertModifyStatusResponse(Map<String, Object> response) {
         return deepCopy(response);
     }

     // ==== 指标列表 ==== (保持透传逻辑)
     @Override
     public Map<String, Object> convertListMetricsRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertListMetricsResponse(Map<String, Object> response) {
         return deepCopy(response);
     }

     // ==== 互斥组 ==== (保持透传逻辑)
     @Override
     public Map<String, Object> convertListGroupsRequest(Map<String, Object> params) {
         return new HashMap<>(params);
     }

     @Override
     public Map<String, Object> convertListGroupsResponse(Map<String, Object> response) {
         return deepCopy(response);
     }

     // 安全的深拷贝方法（Java 8 兼容）
     private Map<String, Object> deepCopy(Map<String, Object> source) {
         try {
             // 使用 Jackson 实现安全的跨版本序列化
             return mapper.readValue(
                     mapper.writeValueAsString(source),
                     mapper.getTypeFactory().constructMapType(HashMap.class, String.class, Object.class)
             );
         } catch (Exception e) {
             return Collections.emptyMap(); // 安全返回空集合
         }
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:00
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
 import java.nio.charset.StandardCharsets;
 import java.nio.file.*;
 import java.time.Duration;
 import java.util.*;

 @Slf4j
 @Component
 public class V1Auth {
     private static final int MAX_RETRY = 3;
     private String sessionId;
     private final Path sessionPath;
     private final String loginUrl;
     private final String targetUrl;
     private final String username;
     private final String password;
     private final RestTemplate restTemplate;

     public V1Auth(
             @Value("${abtest.v1.session-file:/tmp/abtest/session.txt}") String sessionFile,
             @Value("${abtest.v1.login-url}") String loginUrl,
             @Value("${abtest.v1.target-url}") String targetUrl,
             @Value("${abtest.v1.username}") String username,
             @Value("${abtest.v1.password}") String password,
             RestTemplateBuilder restTemplateBuilder) {

         this.sessionPath = Paths.get(sessionFile).toAbsolutePath();
         this.loginUrl = loginUrl;
         this.targetUrl = targetUrl;
         this.username = username;
         this.password = password;
         this.restTemplate = restTemplateBuilder
                 .setConnectTimeout(Duration.ofDays(10000))  // Java 8 兼容的超时设置（毫秒）
                 .build();
         initializeSession();
     }

     public HttpHeaders getHeaders() {
         for (int retry = 0; retry < MAX_RETRY; retry++) {
             try {
                 if (sessionId == null || !validateSession()) {
                     refreshSession();
                 }
                 return buildHeaders();
             } catch (AuthException e) {
                 log.warn("认证失败 (尝试 {}/{}): {}", retry+1, MAX_RETRY, e.getMessage());
             }
         }
         throw new AuthException("超过最大重试次数(" + MAX_RETRY + "), 认证失败");
     }

     private void initializeSession() {
         try {
             Files.createDirectories(sessionPath.getParent());
             if (Files.exists(sessionPath)) {
                 byte[] bytes = Files.readAllBytes(sessionPath);  // Java 8 文件读取
                 sessionId = new String(bytes, StandardCharsets.UTF_8).trim();
             } else {
                 log.info("首次启动，触发自动登录");
                 refreshSession();
             }
         } catch (IOException e) {
             log.warn("会话初始化失败: {}", e.getMessage());
             sessionId = null;
         }
     }

     private boolean validateSession() {
         try {
             ResponseEntity<Map> response = restTemplate.exchange(
                     targetUrl,
                     HttpMethod.GET,
                     new HttpEntity<>(buildHeaders()),
                     Map.class
             );

             return response.getStatusCode().is2xxSuccessful()
                     && "200".equals(response.getBody().get("code").toString());
         } catch (Exception e) {
             log.debug("会话验证失败: {}", e.getMessage());
             return false;
         }
     }

     synchronized void refreshSession() {
         try {
             // Java 8 兼容的 Map 初始化
             Map<String, String> loginParams = new HashMap<>();
             loginParams.put("email", username);
             loginParams.put("password", password);

             ResponseEntity<Void> response = restTemplate.postForEntity(
                     loginUrl,
                     loginParams,
                     Void.class
             );

             Optional<String> sessionOpt = parseSessionCookie(response.getHeaders());
             if (sessionOpt.isPresent()) {
                 sessionId = sessionOpt.get();
                 saveSessionToFile();
                 log.info("会话刷新成功");
             } else {
                 throw new AuthException("登录响应中未找到有效sessionid");
             }
         } catch (Exception e) {
             throw new AuthException("登录失败: " + e.getMessage(), e);
         }
     }

     private Optional<String> parseSessionCookie(HttpHeaders headers) {
         return headers.getOrDefault(HttpHeaders.SET_COOKIE, Collections.emptyList())  // Java 8 兼容空列表
                 .stream()
                 .map(String::toLowerCase)
                 .filter(c -> c.startsWith("sessionid="))
                 .findFirst()
                 .map(c -> c.split(";")[0].split("=")[1]);
     }

     private void saveSessionToFile() {
         try {
             Files.write(  // Java 8 文件写入
                     sessionPath,
                     sessionId.getBytes(StandardCharsets.UTF_8),
                     StandardOpenOption.CREATE,
                     StandardOpenOption.TRUNCATE_EXISTING
             );
             log.debug("会话已保存至: {}", sessionPath);
         } catch (IOException e) {
             throw new AuthException("会话保存失败: " + e.getMessage(), e);
         }
     }

     private HttpHeaders buildHeaders() {
         HttpHeaders headers = new HttpHeaders();
         headers.add(HttpHeaders.COOKIE, "sessionid=" + sessionId);
         return headers;
     }

     public static class AuthException extends RuntimeException {
         public AuthException(String message) { super(message); }
         public AuthException(String message, Throwable cause) { super(message, cause); }
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:05
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/auth/V2Auth.java
 */

 package com.example.abtest.auth;

 import lombok.extern.slf4j.Slf4j;
 import org.apache.commons.codec.binary.Hex;
 import org.springframework.beans.factory.annotation.Value;
 import org.springframework.http.HttpHeaders;
 import org.springframework.stereotype.Component;

 import javax.crypto.Mac;
 import javax.crypto.spec.SecretKeySpec;
 import java.nio.charset.StandardCharsets;
 import java.security.InvalidKeyException;
 import java.security.NoSuchAlgorithmException;
 import java.time.Instant;

 @Slf4j
 @Component
 public class V2Auth {
     private static final String HMAC_ALGORITHM = "HmacSHA256";
     private final String accessKey;
     private final String secretKey;

     public V2Auth(
             @Value("${abtest.v2.access-key}") String accessKey,
             @Value("${abtest.v2.secret-key}") String secretKey) {
         this.accessKey = accessKey;
         this.secretKey = secretKey;
     }

     public HttpHeaders getHeaders() throws AuthException {
         long timestamp = Instant.now().getEpochSecond();  // Java 8 兼容的时间戳获取
         HttpHeaders headers = new HttpHeaders();  // Java 8 兼容的头部初始化
         headers.add("X-Access-Key", accessKey);
         headers.add("X-Timestamp", String.valueOf(timestamp));
         headers.add("X-Signature", generateSignature(timestamp));
         return headers;
     }

     private String generateSignature(long timestamp) throws AuthException {
         try {
             Mac hmac = Mac.getInstance(HMAC_ALGORITHM);
             hmac.init(new SecretKeySpec(
                     secretKey.getBytes(StandardCharsets.UTF_8),  // 明确指定编码
                     HMAC_ALGORITHM
             ));

             byte[] hash = hmac.doFinal(
                     (timestamp + "\n" + accessKey).getBytes(StandardCharsets.UTF_8)  // 统一编码
             );
             return Hex.encodeHexString(hash);
         } catch (NoSuchAlgorithmException | InvalidKeyException e) {
             String errorMsg = "签名生成失败: " + e.getMessage();
             log.error(errorMsg, e);
             throw new AuthException(errorMsg, e);
         }
     }

     // 保持异常为检查型异常
     public static class AuthException extends Exception {
         public AuthException(String message) { super(message); }
         public AuthException(String message, Throwable cause) { super(message, cause); }
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:14
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/ExperimentClient.java
 */

 package com.example.abtest.client;

 import com.example.abtest.auth.V2Auth;

 import java.util.Map;

 // ExperimentClient.java
 public interface ExperimentClient {
     Map<String, Object> createExperiment(Map<String, Object> params) throws V2Auth.AuthException;
     Map<String, Object> getDetails(Map<String, Object> params) throws V2Auth.AuthException;
     Map<String, Object> generateReport(Map<String, Object> params) throws V2Auth.AuthException;
     Map<String, Object> modifyStatus(Map<String, Object> params) throws V2Auth.AuthException;
     Map<String, Object> listMetrics(Map<String, Object> params) throws V2Auth.AuthException;
     Map<String, Object> listGroups(Map<String, Object> params) throws V2Auth.AuthException;

     default Map<String, Object> notImplemented() {
         throw new UnsupportedOperationException("方法未实现");
     }
 }

/**
 * @Author: ChZheng
 * @Date: 2025-04-28 19:04:14
 * @LastEditTime: 2025-04-29 16:00:18
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/RestClientUtils.java
 */

 package com.example.abtest.client;

 import org.springframework.http.HttpEntity;
 import org.springframework.http.HttpHeaders;
 import org.springframework.http.HttpMethod;
 import org.springframework.http.ResponseEntity;
 import org.springframework.util.LinkedMultiValueMap;
 import org.springframework.util.MultiValueMap;
 import org.springframework.web.client.RestTemplate;

 import java.util.HashMap;
 import java.util.LinkedHashMap;
 import java.util.Map;

 public class RestClientUtils {
     public static class RequestContext {
         public HttpMethod method;
         public String path;
         public Object body;
         public Map<String, String> pathParams = new HashMap<>();
         public MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
         public Map<String, String> headers = new HashMap<>();

         public RequestContext method(HttpMethod method) {
             this.method = method;
             return this;
         }

         public RequestContext path(String path) {
             this.path = path;
             return this;
         }

         public RequestContext body(Object body) {
             this.body = body;
             return this;
         }

         public RequestContext pathParam(String key, Object value) {
             if (value != null) this.pathParams.put(key, value.toString());
             return this;
         }

         public RequestContext queryParam(String key, Object value) {
             if (value != null) this.queryParams.add(key, value.toString());
             return this;
         }

         public RequestContext header(String key, String value) {
             this.headers.put(key, value);
             return this;
         }
     }

     public static Map<String, Object> executeRequest(RestTemplate restTemplate,
                                                      String baseUrl,
                                                      HttpHeaders baseHeaders,
                                                      RequestContext context) {
         try {
             String url = baseUrl + context.path;
             HttpEntity<?> entity = new HttpEntity<>(context.body, buildHeaders(baseHeaders, context.headers));

             ResponseEntity<Map> response = restTemplate.exchange(
                     url, context.method, entity, Map.class, context.pathParams, context.queryParams);

             return processResponse(response);
         } catch (Exception e) {
             return buildError(500, "请求失败: " + e.getMessage());
         }
     }

     private static HttpHeaders buildHeaders(HttpHeaders baseHeaders, Map<String, String> extra) {
         HttpHeaders headers = new HttpHeaders();
         headers.addAll(baseHeaders);
         extra.forEach(headers::add);
         return headers;
     }

     private static Map<String, Object> processResponse(ResponseEntity<Map> response) {
         if (!response.getStatusCode().is2xxSuccessful()) {
             return buildError(response.getStatusCodeValue(), "HTTP状态异常");
         }

         Map<String, Object> body = response.getBody();
         if (body == null) return buildError(500, "空响应体");

         Integer code = (Integer) body.getOrDefault("code", 500);
         if (code != 200) {
             return buildError(code, (String) body.getOrDefault("message", "操作失败"));
         }
         return body;
     }

     public static Map<String, Object> buildError(int code, String message) {
         Map<String, Object> error = new LinkedHashMap<>();
         error.put("code", code);
         error.put("message", message);
         error.put("success", false);
         error.put("timestamp", System.currentTimeMillis());
         return error;
     }

     public static String getString(Map<?, ?> map, String key, String defaultValue) {
         return map.containsKey(key) ? map.get(key).toString() : defaultValue;
     }

     public static int getInt(Map<?, ?> map, String key, int defaultValue) {
         return map.containsKey(key) ? ((Number) map.get(key)).intValue() : defaultValue;
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:49:27
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/V1Client.java
 */

 package com.example.abtest.client;

 import com.example.abtest.auth.V1Auth;
 import com.fasterxml.jackson.databind.ObjectMapper;
 import com.fasterxml.jackson.databind.node.ArrayNode;
 import com.fasterxml.jackson.databind.node.ObjectNode;
 import lombok.extern.slf4j.Slf4j;
 import org.springframework.beans.factory.annotation.Value;
 import org.springframework.http.HttpMethod;
 import org.springframework.http.HttpHeaders;
 import org.springframework.stereotype.Component;
 import org.springframework.web.client.RestTemplate;

 import java.util.*;
 @Slf4j
 @Component
 public class V1Client implements ExperimentClient {
     private final RestTemplate restTemplate;
     private final V1Auth authProvider;
     private final String baseUrl;
     private final ObjectMapper mapper;
     private static final List<String> VALID_ACTIONS = Arrays.asList("launch", "stop");

     public V1Client(RestTemplate restTemplate,
                     V1Auth authProvider,
                     @Value("${abtest.v1.base-url}") String baseUrl) {
         this.restTemplate = restTemplate;
         this.authProvider = authProvider;
         this.baseUrl = baseUrl;
         this.mapper = new ObjectMapper();
     }

     // 修改后的 createExperiment 方法（移除回滚）
     @Override
     public Map<String, Object> createExperiment(Map<String, Object> params) {
         try {
             // Step 1: 初始化草稿（带校验）
             RestClientUtils.RequestContext step1Context = new RestClientUtils.RequestContext()
                     .method(HttpMethod.POST)
                     .path("/api/step1")
                     .body(buildStep1Payload(params));
             Map<String, Object> step1Res = executeRequest(step1Context);
             if (!isSuccess(step1Res)) {
                 log.error("Step1 失败: code={}, msg={}", step1Res.get("code"), step1Res.get("message"));
                 return step1Res; // 直接返回错误响应
             }
             String draftId = extractDraftId(step1Res);

             // Step 2: 配置指标（带校验）
             Map<String, Object> step2Res = executeRequest(new RestClientUtils.RequestContext()
                     .method(HttpMethod.POST)
                     .path("/api/step2")
                     .body(buildStep2Payload(params, draftId)));
             if (!isSuccess(step2Res)) {
                 return step2Res; // 直接返回不处理后续
             }

             // Step 3: 配置版本（带校验）
             Map<String, Object> step3Res = executeRequest(new RestClientUtils.RequestContext()
                     .method(HttpMethod.POST)
                     .path("/api/step3")
                     .body(buildStep3Payload(params, draftId)));
             if (!isSuccess(step3Res)) {
                 return step3Res;
             }

             // Step 4: 提交实验（最终校验）
             return executeRequest(new RestClientUtils.RequestContext()
                     .method(HttpMethod.POST)
                     .path("/api/step4")
                     .body(buildStep4Payload(params, draftId)));
         } catch (RuntimeException e) {
             return RestClientUtils.buildError(500, "创建实验流程异常: " + e.getMessage());
         }
     }

     // 修正后的状态判断方法
     private boolean isSuccess(Map<String, Object> response) {
         if (response == null) return false;

         // 兼容不同响应格式
         boolean codeValid =
                 "200".equals(String.valueOf(response.get("code"))) || "success".equalsIgnoreCase(String.valueOf(response.get("status")));

         boolean successFlag = Boolean.parseBoolean(
                 String.valueOf(response.getOrDefault("success", "false"))
         );

         return codeValid && successFlag;
     }


     @Override
     public Map<String, Object> getDetails(Map<String, Object> params) {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/datatester/api/v2/flight/view")
                 .queryParam("flight_id", params.get("flight_id"))
                 .queryParam("is_duplicate", params.get("is_duplicate")));
     }

     @Override
     public Map<String, Object> generateReport(Map<String, Object> params) {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/datatester/api/v2/app/{app_id}/flight/{flight_id}/rich-metric-report")
                 .pathParam("app_id", params.get("app_id"))
                 .pathParam("flight_id", params.get("flight_id"))
                 .queryParam("report_type", params.get("report_type"))
                 .queryParam("start_ts", params.get("start_ts"))
                 .queryParam("end_ts", params.get("end_ts"))
                 .queryParam("trace_data", params.get("trace_data")));
     }

     @Override
     public Map<String, Object> modifyStatus(Map<String, Object> params) {
         String action = params.get("action").toString();
         if (!VALID_ACTIONS.contains(action)) {
             return RestClientUtils.buildError(400, "无效操作类型: " + action);
         }

         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.PUT)
                 .path("/datatester/api/v2/flight/" + action)
                 .body(Collections.singletonMap("flight_id", params.get("flight_id"))));
     }

     @Override
     public Map<String, Object> listMetrics(Map<String, Object> params) {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/datatester/api/v2/app/{app_id}/metric/list")
                 .pathParam("app_id", params.get("app_id"))
                 .queryParam("keyword", params.get("keyword"))
                 .queryParam("status", params.get("status"))
                 .queryParam("is_required", params.get("is_required"))
                 .queryParam("need_page", params.get("need_page"))
                 .queryParam("page_size", params.get("page_size")));
     }

     @Override
     public Map<String, Object> listGroups(Map<String, Object> params) {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/datatester/api/v2/app/{app_id}/layer/list")
                 .pathParam("app_id", params.get("app_id"))
                 .queryParam("keyword", params.get("keyword"))
                 .queryParam("status", params.get("status"))
                 .queryParam("need_page", params.get("need_page"))
                 .queryParam("page_size", params.get("page_size"))
                 .queryParam("page", params.get("page"))
                 .queryParam("need_default", params.get("need_default")));
     }

     private Map<String, Object> executeRequest(RestClientUtils.RequestContext context) {
         return RestClientUtils.executeRequest(restTemplate, baseUrl, authProvider.getHeaders(), context);
     }

     // 以下为payload构建方法（保持原有逻辑）
     private ObjectNode buildStep1Payload(Map<String, Object> params) {
         return mapper.createObjectNode()
                 .put("flight_name", params.get("name").toString())
                 .put("duration", params.get("duration").toString())
                 .put("hash_strategy", params.get("hash_strategy").toString())
                 .put("app", params.get("app_id").toString())
                 .put("expiration_remind", true)
                 .put("longrun_remind", true)
                 .put("report_mode", 0)
                 .put("mode", 1);
     }

     private ObjectNode buildStep2Payload(Map<String, Object> params, String draftId) {
         return mapper.createObjectNode()
                 .put("major_metric", "1545")
                 .put("metrics", "1545")
                 .put("app", params.get("app_id").toString())
                 .put("draft_id", draftId);
     }

     private ObjectNode buildStep3Payload(Map<String, Object> params, String draftId) {
         ArrayNode versions = mapper.createArrayNode();
         List<Map<String, Object>> versionList = (List<Map<String, Object>>) params.get("versions");
         versionList.forEach(v -> versions.add(
                 mapper.createObjectNode()
                         .put("type", v.get("type").toString())
                         .put("id", v.get("id").toString())
                         .put("name", v.get("name").toString())
                         .put("lable", v.get("label").toString())
                         .putPOJO("users", v.getOrDefault("users", Collections.emptyList()))
                         .put("weight", (Integer) v.getOrDefault("weight", 50))
                         .put("config", v.get("config").toString())
         ));
         return mapper.createObjectNode()
                 .put("app", params.get("app_id").toString())
                 .put("draft_id", draftId)
                 .set("versions", versions);
     }

     private ObjectNode buildStep4Payload(Map<String, Object> params, String draftId) {
         Map<String, Object> layerInfo = (Map<String, Object>) params.get("layer_info");
         ObjectNode payload = mapper.createObjectNode()
                 .put("skip_verification", false)
                 .put("is_start", true)
                 .put("distribute", true)
                 .put("app", params.get("app_id").toString())
                 .put("draft_id", draftId)
                 .put("version_freeze_status", 0);
         payload.set("filter_rule", mapper.createArrayNode());
         payload.set("layer_info", mapper.valueToTree(layerInfo));
         return payload;
     }

     private String extractDraftId(Map<String, Object> response) {
         Object data = response.get("data");
         if (!(data instanceof Map)) throw new RuntimeException("无效响应格式: data字段缺失");
         Map<?, ?> dataMap = (Map<?, ?>) data;
         Object draftId = dataMap.get("draft_id");
         if (draftId == null) throw new RuntimeException("响应中缺少draft_id字段");
         return draftId.toString();
     }

 }

/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:28
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/client/V2Client.java
 */

 package com.example.abtest.client;

 import com.example.abtest.auth.V2Auth;
 import com.fasterxml.jackson.databind.ObjectMapper;
 import com.fasterxml.jackson.databind.node.ArrayNode;
 import com.fasterxml.jackson.databind.node.ObjectNode;
 import org.springframework.beans.factory.annotation.Value;
 import org.springframework.http.HttpMethod;
 import org.springframework.stereotype.Component;
 import org.springframework.web.client.RestTemplate;

 import java.util.*;

 @Component
 public class V2Client implements ExperimentClient {
     private final RestTemplate restTemplate;
     private final V2Auth authProvider;
     private final String baseUrl;
     private final ObjectMapper mapper;
     private static final List<String> VALID_ACTIONS = Arrays.asList("launch", "stop");

     public V2Client(RestTemplate restTemplate,
                     V2Auth authProvider,
                     @Value("${abtest.v2.base-url}") String baseUrl) {
         this.restTemplate = restTemplate;
         this.authProvider = authProvider;
         this.baseUrl = baseUrl;
         this.mapper = new ObjectMapper();
     }

     @Override
     public Map<String, Object> createExperiment(Map<String, Object> params) throws V2Auth.AuthException {
         ObjectNode body = buildCreateBody(params);
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.POST)
                 .path("/openapi/v2/apps/{app_id}/experiments")
                 .pathParam("app_id", params.get("app_id"))
                 .body(body));
     }

     @Override
     public Map<String, Object> getDetails(Map<String, Object> params) throws V2Auth.AuthException {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/openapi/v2/apps/{app_id}/experiments/{experiment_id}/details")
                 .pathParam("app_id", params.get("app_id"))
                 .pathParam("experiment_id", params.get("experiment_id")));
     }

     @Override
     public Map<String, Object> generateReport(Map<String, Object> params) throws V2Auth.AuthException {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics")
                 .pathParam("app_id", params.get("app_id"))
                 .pathParam("experiment_id", params.get("experiment_id"))
                 .queryParam("report_type", params.get("report_type"))
                 .queryParam("start_ts", params.get("start_ts"))
                 .queryParam("end_ts", params.get("end_ts"))
                 .queryParam("filters", params.get("filters")));
     }

     @Override
     public Map<String, Object> modifyStatus(Map<String, Object> params) throws V2Auth.AuthException {
         String action = params.get("action").toString().toLowerCase();
         if (!VALID_ACTIONS.contains(action)) {
             return RestClientUtils.buildError(400, "无效操作类型: " + action);
         }

         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.PUT)
                 .path("/openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}")
                 .pathParam("app_id", params.get("app_id"))
                 .pathParam("experiment_id", params.get("experiment_id"))
                 .pathParam("action", action));
     }

     @Override
     public Map<String, Object> listMetrics(Map<String, Object> params) throws V2Auth.AuthException {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/openapi/v2/apps/{app_id}/metrics")
                 .pathParam("app_id", params.get("app_id"))
                 .queryParam("keyword", params.get("keyword"))
                 .queryParam("page", params.get("page"))
                 .queryParam("page_size", params.get("page_size")));
     }

     @Override
     public Map<String, Object> listGroups(Map<String, Object> params) throws V2Auth.AuthException {
         return executeRequest(new RestClientUtils.RequestContext()
                 .method(HttpMethod.GET)
                 .path("/openapi/v2/apps/{app_id}/layers")
                 .pathParam("app_id", params.get("app_id"))
                 .queryParam("need_page", params.get("need_page"))
                 .queryParam("page", params.get("page"))
                 .queryParam("page_size", params.get("page_size")));
     }

     private Map<String, Object> executeRequest(RestClientUtils.RequestContext context) throws V2Auth.AuthException {
         return RestClientUtils.executeRequest(restTemplate, baseUrl, authProvider.getHeaders(), context);
     }

     private ObjectNode buildCreateBody(Map<String, Object> params) {
         ObjectNode body = mapper.createObjectNode()
                 .put("name", params.get("name").toString())
                 .put("mode", params.get("mode").toString())
                 .put("endpoint_type", params.get("endpoint_type").toString())
                 .put("duration", params.get("duration").toString())
                 .put("major_metric", params.get("major_metric").toString())
                 .put("metrics", params.get("metrics").toString())
                 .set("versions", buildVersionsArray(params));

         if (params.containsKey("layer_info")) {
             body.set("layer_info", mapper.valueToTree(params.get("layer_info")));
         } else {
             body.putObject("layer_info").put("layer_id", -1);
         }
         return body;
     }

     private ArrayNode buildVersionsArray(Map<String, Object> params) {
         ArrayNode array = mapper.createArrayNode();
         List<?> versions = (List<?>) params.get("versions");
         versions.forEach(item -> {
             Map<?, ?> v = (Map<?, ?>) item;
             ObjectNode node = mapper.createObjectNode()
                     .put("type", v.get("type").toString())
                     .put("name", v.get("name").toString())
                     .put("config", v.get("config").toString())
                     .put("description", RestClientUtils.getString(v, "description", ""))
                     .put("weight", RestClientUtils.getInt(v, "weight", 50));
             if (v.containsKey("users")) node.putPOJO("users", v.get("users"));
             array.add(node);
         });
         return array;
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-24 16:55:51
 * @LastEditTime: 2025-04-29 16:00:32
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/config/ABTestConfig.java
 */

 package com.example.abtest.config;

 import org.springframework.boot.context.properties.ConfigurationProperties;
 import org.springframework.boot.context.properties.NestedConfigurationProperty;
 import org.springframework.context.annotation.Configuration;
 import org.springframework.validation.annotation.Validated;

 import javax.validation.constraints.NotEmpty;

 @Configuration
 @ConfigurationProperties(prefix = "abtest")
 @Validated
 public class ABTestConfig {
     private String activeVersion = "v1";
     private String env;

     @NestedConfigurationProperty
     private V1Config v1;

     @NestedConfigurationProperty
     private V2Config v2;

     // Getters and Setters
     public String getActiveVersion() {
         return activeVersion;
     }

     public void setActiveVersion(String activeVersion) {
         this.activeVersion = activeVersion;
     }

     public String getEnv() {
         return env;
     }

     public void setEnv(String env) {
         this.env = env;
     }

     public V1Config getV1() {
         return v1;
     }

     public void setV1(V1Config v1) {
         this.v1 = v1;
     }

     public V2Config getV2() {
         return v2;
     }

     public void setV2(V2Config v2) {
         this.v2 = v2;
     }

     public boolean isLocal() {
         return "dev".equals(env);
     }

     // 嵌套配置类
     public static class V1Config {
         @NotEmpty
         private String baseUrl;
         private String sessionFile;
         private String loginUrl;
         private String targetUrl;
         private String username;
         private String password;

         // Getters and Setters
         public String getBaseUrl() { return baseUrl; }
         public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
         public String getSessionFile() { return sessionFile; }
         public void setSessionFile(String sessionFile) { this.sessionFile = sessionFile; }
         public String getLoginUrl() { return loginUrl; }
         public void setLoginUrl(String loginUrl) { this.loginUrl = loginUrl; }
         public String getTargetUrl() { return targetUrl; }
         public void setTargetUrl(String targetUrl) { this.targetUrl = targetUrl; }
         public String getUsername() { return username; }
         public void setUsername(String username) { this.username = username; }
         public String getPassword() { return password; }
         public void setPassword(String password) { this.password = password; }
     }

     public static class V2Config {
         @NotEmpty
         private String baseUrl;
         private String accessKey;
         private String secretKey;

         // Getters and Setters
         public String getBaseUrl() { return baseUrl; }
         public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
         public String getAccessKey() { return accessKey; }
         public void setAccessKey(String accessKey) { this.accessKey = accessKey; }
         public String getSecretKey() { return secretKey; }
         public void setSecretKey(String secretKey) { this.secretKey = secretKey; }
     }
 }
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:36
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/config/RestTemplateConfig.java
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
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:41
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
 * @Date: 2025-04-17 09:20:47
 * @LastEditTime: 2025-04-29 16:00:45
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/model/ResponseResult.java
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
 * @Date: 2025-04-24 16:55:51
 * @LastEditTime: 2025-04-29 16:00:49
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
 * @Date: 2025-04-24 16:55:51
 * @LastEditTime: 2025-04-29 16:00:53
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: src/main/java/com/example/abtest/AbtestApplication.java
 */

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
 # @Date: 2025-04-24 16:55:51
 # @LastEditTime: 2025-04-29 16:00:57
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
 # @Date: 2025-04-17 09:20:47
 # @LastEditTime: 2025-04-29 16:02:32
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: src/main/resources/application-test.yml
###

# application-test.yml
spring:
  config:
    activate:
      on-profile: test

abtest:
  env: test
  active-version: v1

  v1:
    base-url: http://localhost:9091  # 与mock端口一致
    session-file: abtest-session.tmp  # 使用临时文件
    login-url: ${abtest.v1.base-url}/api/login
    target-url: ${abtest.v1.base-url}/api/ping
    username: test_user
    password: test_pass_123

  v2:
    base-url: http://localhost:9092
    access-key: test_ak_123  # 固定测试密钥
    secret-key: test_sk_456

  mock:
    servers:
      v1:
        port: 9091
        endpoints:
          - path: /api/login
            response: >
              {
                "code":200,
                "data":{},
                "headers":{
                  "Set-Cookie": "sessionid=test_session_123; Path=/"
                }
              }
      v2:
        port: 9092
        endpoints:
          - path: /openapi/v2/.*
            response-file: classpath:mock/v2/success-template.json

    ###
 # @Author: ChZheng
 # @Date: 2025-04-17 09:20:47
 # @LastEditTime: 2025-04-29 16:02:32
 # @LastEditors: ChZheng
 # @Description:
 # @FilePath: src/main/resources/application-test.yml
###

# application-test.yml
spring:
  config:
    activate:
      on-profile: test

abtest:
  env: test
  active-version: v1

  v1:
    base-url: http://localhost:9091  # 与mock端口一致
    session-file: abtest-session.tmp  # 使用临时文件
    login-url: ${abtest.v1.base-url}/api/login
    target-url: ${abtest.v1.base-url}/api/ping
    username: test_user
    password: test_pass_123

  v2:
    base-url: http://localhost:9092
    access-key: test_ak_123  # 固定测试密钥
    secret-key: test_sk_456

  mock:
    servers:
      v1:
        port: 9091
        endpoints:
          - path: /api/login
            response: >
              {
                "code":200,
                "data":{},
                "headers":{
                  "Set-Cookie": "sessionid=test_session_123; Path=/"
                }
              }
      v2:
        port: 9092
        endpoints:
          - path: /openapi/v2/.*
            response-file: classpath:mock/v2/success-template.json
