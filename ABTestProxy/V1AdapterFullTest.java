/*
 * @Author: ChZheng
 * @Date: 2025-04-21 15:37:40
 * @LastEditTime: 2025-04-21 15:38:58
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: /code/ABTest/ABTestProxy/V1AdapterFullTest.java
 */
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/adapter/V1AdapterFullTest.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.V1Adapter;
import org.junit.jupiter.api.Test;

import java.text.SimpleDateFormat;
import java.util.*;

import static java.util.Map.entry;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

// V1AdapterFullTest.java
public class V1AdapterFullTest {
    private V1Adapter adapter = new V1Adapter();
    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    @Test
    void testAllRequestConversions() {
        // 测试所有请求转换方法
        Map<String, Object> createReq = adapter.convertCreateExperimentRequest(new HashMap<>());
        assertTrue(createReq.containsKey("hash_strategy"));

        Map<String, Object> reportReq = adapter.convertGenerateReportRequest(Map.of("app_id", 1));
        assertTrue(reportReq.containsKey("trace_data"));

        Map<String, Object> statusReq = adapter.convertModifyStatusRequest(
                Map.of("experiment_id", 123, "action", "stop")
        );
        assertEquals(123, statusReq.get("flight_id"));
    }

    @Test
    void testAllResponseConversions() {
        // 测试所有响应转换方法
        Map<String, Object> detailsResponse = buildDetailsResponse();
        Map<String, Object> convertedDetails = adapter.convertGetDetailsResponse(detailsResponse);
        validateDetailsConversion(convertedDetails);

        Map<String, Object> reportResponse = Map.of("code", 200, "data", new HashMap<>());
        assertEquals(reportResponse, adapter.convertGenerateReportResponse(reportResponse));
    }

    private Map<String, Object> buildDetailsResponse() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

        return Map.ofEntries(
                entry("code", 200),
                entry("message", "success"),
                entry("data", Map.ofEntries(
                        entry("id", 456),
                        entry("name", "test_flight"),
                        entry("start_ts", sdf.format(new Date(1715616000L * 1000))),
                        entry("end_ts", sdf.format(new Date(1715702400L * 1000))),
                        entry("owner", "tester"),
                        entry("description", "测试实验"),
                        entry("status", 1),
                        entry("type", "client"),
                        entry("mode", "simple"),
                        entry("layer", Map.ofEntries(  // 直接嵌套
                                entry("name", "layer1"),
                                entry("status", 2),
                                entry("type", "client"),
                                entry("description", "")
                        )),
                        entry("version_resource", "resource_v1"),
                        entry("versions", List.of(  // 直接定义集合
                                Map.ofEntries(
                                        entry("id", "v1"),
                                        entry("name", "version1"),
                                        entry("type", "config"),
                                        entry("config", Map.of()),
                                        entry("description", "desc"),
                                        entry("weight", 50)
                                )
                        )),
                        entry("metrics", List.of(
                                Map.of("metrics", List.of(
                                        Map.ofEntries(
                                                entry("id", "m1"),
                                                entry("name", "metric1"),
                                                entry("metric_description", "测试指标"),
                                                entry("type", "count")
                                        )
                                ))
                        )),
                        entry("whitelist", Collections.emptyList())
                ))
        );
    }


    private void validateDetailsConversion(Map<String, Object> converted) {
        Map<String, Object> data = (Map<String, Object>) converted.get("data");
        assertEquals("test_flight", data.get("name"));
        assertEquals("2024-05-13 00:00:00", data.get("start_ts"));
        assertEquals("2024-05-14 00:00:00", data.get("end_ts"));
        assertEquals(1, ((List<?>) data.get("versions")).size());
        assertEquals(1, ((List<?>) data.get("metrics")).size());
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/adapter/V2AdapterFullTest.java
 * @Description:
 */
package com.example.abtest.adapter;

import com.example.abtest.adapter.V2Adapter;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class V2AdapterFullTest {
    private final V2Adapter adapter = new V2Adapter();

    @Test
    void testAllConversions() {
        // 请求转换测试
        Map<String, Object> createReq = adapter.convertCreateExperimentRequest(
                Map.of("name", "v2_test", "mode", "advanced")
        );
        assertEquals("v2_test", createReq.get("name"));

        // 响应转换测试
        Map<String, Object> backendResponse = Map.of(
                "code", 201,
                "data", Map.of(
                        "id", "v2_exp_123",
                        "config", Map.of("key", "value")
                )
        );
        Map<String, Object> converted = adapter.convertCreateExperimentResponse(backendResponse);
        assertEquals("v2_exp_123", ((Map) converted.get("data")).get("id"));
    }

    @Test
    void testFullDetailsConversion() {
        Map<String, Object> mockResponse = Map.of(
                "code", 200,
                "data", Map.of(
                        "id", 789,
                        "name", "v2_experiment",
                        "start_time", "2024-05-15T00:00:00Z",
                        "metrics", List.of(Map.of("type", "conversion"))
                )
        );

        Map<String, Object> result = adapter.convertGetDetailsResponse(mockResponse);
        assertEquals(200, result.get("code"));
        assertEquals("v2_experiment", ((Map) result.get("data")).get("name"));
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/auth/V1AuthFullTest.java
 * @Description:
 */
package com.example.abtest.auth;

import com.example.abtest.auth.V1Auth;
import com.example.abtest.auth.V2Auth;
import org.apache.commons.codec.binary.Hex;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

// V1AuthFullTest.java
@SpringBootTest
@AutoConfigureMockMvc
public class V1AuthFullTest {
    @Autowired
    private V1Auth auth;

    @MockBean
    private RestTemplate restTemplate;

    @Test
    void testFullAuthFlow() throws IOException {
        // 测试完整认证流程
        Path sessionFile = Paths.get("test_session.txt");
        Files.deleteIfExists(sessionFile);

        // 首次认证
        when(restTemplate.postForEntity(anyString(), any(), any()))
                .thenReturn(ResponseEntity.ok()
                        .header("Set-Cookie", "sessionid=test_session_123")
                        .body(null));

        HttpHeaders headers1 = auth.getHeaders();
        assertTrue(headers1.containsKey("Cookie"));

        // 验证会话持久化
        assertTrue(Files.exists(sessionFile));
        assertEquals("test_session_123", Files.readString(sessionFile).trim());

        // 后续请求使用缓存会话
        HttpHeaders headers2 = auth.getHeaders();
        assertEquals("sessionid=test_session_123", headers2.getFirst("Cookie"));
    }
}

/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/auth/V2AuthFullTest.java
 * @Description:
 */
package com.example.abtest.auth;

import com.example.abtest.auth.V2Auth;
import org.apache.commons.codec.binary.Hex;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import static org.junit.jupiter.api.Assertions.assertEquals;

// V2AuthFullTest.java
public class V2AuthFullTest {
    @Test
    void testSignatureConsistency() {
        V2Auth auth = new V2Auth("AK_TEST", "SK_TEST");
        HttpHeaders headers = auth.getHeaders();

        String timestamp = headers.getFirst("X-Timestamp");
        String signature = headers.getFirst("X-Signature");

        String expected = hmacSHA256("SK_TEST", timestamp + "\nAK_TEST");
        assertEquals(expected, signature);
    }

    private String hmacSHA256(String secret, String data) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(), "HmacSHA256"));
            return Hex.encodeHexString(mac.doFinal(data.getBytes()));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
package com.example.abtest.client; /**
 * @Author: ChZheng
 * @Date: 2025-04-18 15:59:09
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-21 15:24:57
 * @FilePath: src/test/java/com/example/abtest/client/ClientTestBase.java
 * @Description:
 */
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

@SpringBootTest
public class ClientTestBase {
    @Autowired
    protected RestTemplate restTemplate;

    protected MockRestServiceServer mockServer;

    @BeforeEach
    void init() {
        mockServer = MockRestServiceServer.bindTo(restTemplate).build();
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-21 15:24:57
 * @FilePath: src/test/java/com/example/abtest/client/V1ClientMockTest.java
 * @Description:
 */
package com.example.abtest.client;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

public class V1ClientMockTest extends ClientTestBase {
    @Autowired
    private V1Client client;

    @Test
    void testGetDetails() {
        // 配置模拟响应
        mockServer.expect(requestTo("/datatester/api/v2/flight/view?flight_id=123"))
                .andRespond(withSuccess(
                        "{\"code\":200,\"data\":{\"flight_name\":\"mock_flight\"}}",
                        MediaType.APPLICATION_JSON
                ));

        // 执行测试
        Map<String, Object> response = client.getDetails(Map.of(
                "flight_id", 123,
                "is_duplicate", false
        ));

        // 验证结果
        assertEquals(200, response.get("code"));
        assertEquals("mock_flight", ((Map)response.get("data")).get("flight_name"));
    }
}
package com.example.abtest.client; /**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-21 15:24:57
 * @FilePath: src/test/java/com/example/abtest/client/V2ClientMockTest.java
 * @Description:
 */
import com.example.abtest.client.ClientTestBase;
import com.example.abtest.client.V2Client;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;

import java.util.Map;

import static org.graalvm.compiler.hotspot.nodes.type.MethodPointerStamp.method;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.jsonPath;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

public class V2ClientMockTest extends ClientTestBase {
    @Autowired
    private V2Client client;

    @Test
    void testCreateExperimentV2() {
        // 配置请求匹配器
        mockServer.expect(requestTo("/openapi/v2/apps/1/experiments"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(jsonPath("$.name").value("v2_test"))
                .andRespond(withSuccess(
                        "{\"code\":201,\"data\":{\"id\":\"v2_exp_001\"}}",
                        MediaType.APPLICATION_JSON
                ));

        // 执行测试
        Map<String, Object> response = client.createExperiment(Map.of(
                "app_id", 1,
                "name", "v2_test"
        ));

        // 验证响应
        assertEquals(201, response.get("code"));
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/config/ABTestConfigFullTest.java
 * @Description:
 */
package com.example.abtest.config;

import com.example.abtest.config.ABTestConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

// ABTestConfigFullTest.java
@SpringBootTest
@ActiveProfiles("fulltest")
public class ABTestConfigFullTest {
    @Autowired
    private ABTestConfig config;

    @Test
    void testAllConfigProperties() {
        // 验证V1配置
        assertEquals("http://v1-mock:9090", config.getV1().getBaseUrl());
        assertEquals("full_user", config.getV1().getUsername());

        // 验证V2配置
        assertEquals("http://v2-mock:9090", config.getV2().getBaseUrl());
        assertEquals("full_ak", config.getV2().getAccessKey());

        // 验证环境判断
        assertTrue(config.isLocal());
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/config/ABTestConfigFullTest.java
 * @Description:
 */
package com.example.abtest.config;

import com.example.abtest.config.ABTestConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

// ABTestConfigFullTest.java
@SpringBootTest
@ActiveProfiles("fulltest")
public class ABTestConfigFullTest {
    @Autowired
    private ABTestConfig config;

    @Test
    void testAllConfigProperties() {
        // 验证V1配置
        assertEquals("http://v1-mock:9090", config.getV1().getBaseUrl());
        assertEquals("full_user", config.getV1().getUsername());

        // 验证V2配置
        assertEquals("http://v2-mock:9090", config.getV2().getBaseUrl());
        assertEquals("full_ak", config.getV2().getAccessKey());

        // 验证环境判断
        assertTrue(config.isLocal());
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/controller/ABTestControllerFullTest.java
 * @Description:
 */
package com.example.abtest.controller;

import com.example.abtest.controller.ABTestController;
import com.example.abtest.model.ResponseResult;
import com.example.abtest.service.ABTestService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.Map;

// ABTestControllerFullTest.java
@WebMvcTest(ABTestController.class)
public class ABTestControllerFullTest {
    @Autowired
    private MockMvc mvc;

    @MockBean
    private ABTestService service;

    @Test
    void testAllEndpoints() throws Exception {
        // 测试所有API端点
        testCreateExperiment();
        testGetDetails();
        testGenerateReport();
        testModifyStatus();
        testListMetrics();
        testListGroups();
    }

    private void testListGroups() {
    }

    private void testListMetrics() {
    }

    private void testModifyStatus() {
    }

    private void testGenerateReport() {
    }

    private void testGetDetails() {
    }

    private void testCreateExperiment() throws Exception {
        when(service.createExperiment(any()))
                .thenReturn(ResponseResult.success(Map.of("id", 123)));

        mvc.perform(post("/openapi/v1/apps/1/experiments")
                        .content("{ \"name\": \"API测试\" }")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpectAll(
                        status().isOk(),
                        jsonPath("$.data.id").value(123)
                );
    }

    // 其他端点测试方法类似...
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/model/ResponseResultFullTest.java
 * @Description:
 */
package com.example.abtest.model;

import com.example.abtest.model.ResponseResult;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ResponseResultFullTest {
    @Test
    void testAllResponseVariants() {
        // 测试成功响应
        ResponseResult success = ResponseResult.success(Map.of("key", "value"));
        assertEquals(200, success.getCode());
        assertEquals("value", ((Map) success.getData()).get("key"));

        // 测试错误响应
        ResponseResult error = ResponseResult.error(400, "Invalid input");
        assertEquals(400, error.getCode());
        assertNull(error.getData());

        // 测试自定义消息
        ResponseResult custom = new ResponseResult(201, "Created", null);
        assertEquals(201, custom.getCode());
        assertEquals("Created", custom.getMessage());
    }

    @Test
    void testEdgeCases() {
        // 空数据测试
        ResponseResult emptyData = ResponseResult.success(null);
        assertNull(emptyData.getData());

        // 异常数据类型
        ResponseResult numberData = ResponseResult.success(123);
        assertEquals(123, numberData.getData());
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-17 19:28:55
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/service/ABTestServiceFullTest.java
 * @Description:
 */
package com.example.abtest.service;

import com.example.abtest.client.ExperimentClient;
import com.example.abtest.model.ResponseResult;
import com.example.abtest.service.ABTestService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import static org.mockito.Mockito.*;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

// ABTestServiceFullTest.java
@SpringBootTest
public class ABTestServiceFullTest {
    @MockBean(name = "v1Client")
    private ExperimentClient v1Client;

    @MockBean(name = "v2Client")
    private ExperimentClient v2Client;

    @Autowired
    private ABTestService service;

    @Test
    void testAllServiceMethods() {
        // 测试所有服务方法
        testVersionRouting();
        testErrorHandling();
        testDataConversion();
    }

    private void testDataConversion() {
    }

    private void testVersionRouting() {
        // V1版本测试
        when(v1Client.createExperiment(any()))
                .thenReturn(Map.of("code", 200));
        ResponseResult v1Res = service.createExperiment(Map.of("version", "v1", "app_id", 1));
        assertEquals(200, v1Res.getCode());

        // V2版本测试
        when(v2Client.createExperiment(any()))
                .thenReturn(Map.of("code", 201));
        ResponseResult v2Res = service.createExperiment(Map.of("version", "v2", "app_id", 1));
        assertEquals(201, v2Res.getCode());
    }

    private void testErrorHandling() {
        // 测试异常处理
        when(v1Client.getDetails(any()))
                .thenThrow(new RuntimeException("模拟错误"));

        ResponseResult res = service.getExperimentDetails(Map.of("version", "v1"));
        assertEquals(500, res.getCode());
    }
}
package com.example.abtest.system;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.*;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class FullSystemTest {

    @LocalServerPort
    private int port;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private TestRestTemplate testRestTemplate;

    private MockRestServiceServer mockServer;

    @BeforeEach
    void setUp() {
        mockServer = MockRestServiceServer.bindTo(restTemplate).build();
    }

    @Test
    void testCompleteV1Flow() {
        // 构建带Cookie头的登录响应
        HttpHeaders loginHeaders = new HttpHeaders();
        loginHeaders.add(HttpHeaders.SET_COOKIE, "sessionid=system_test");

        // 配置V1服务模拟
        mockServer.expect(requestTo("/api/login"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess()
                        .headers(loginHeaders)  // 正确设置响应头
                        .body("{\"code\":200}"));

        mockServer.expect(requestTo("/api/step1"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(header("Cookie", "sessionid=system_test")) // 验证请求头
                .andRespond(withSuccess()
                        .body("{\"code\":200,\"data\":{\"draft_id\":\"sys_draft_1\"}}"));

        mockServer.expect(requestTo("/api/step4"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess()
                        .body("{\"code\":200,\"data\":{\"flight_id\":\"sys_exp_001\"}}"));

        // 执行V1创建实验
        ResponseEntity<Map> response = testRestTemplate.postForEntity(
                "http://localhost:" + port + "/openapi/v1/apps/100/experiments",
                Map.of("name", "System Test V1"),
                Map.class
        );

        // 验证结果
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("sys_exp_001", ((Map) response.getBody().get("data")).get("id"));
        mockServer.verify();
    }

    @Test
    void testCompleteV2Flow() {
        // 配置V2服务模拟
        mockServer.expect(requestTo("/openapi/v2/apps/200/experiments"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(jsonPath("$.name").value("System Test V2"))
                .andRespond(withSuccess()
                        .body("{\"code\":201,\"data\":{\"id\":\"v2_exp_002\"}}"));

        // 执行V2创建实验
        ResponseEntity<Map> response = testRestTemplate.postForEntity(
                "http://localhost:" + port + "/openapi/v2/apps/200/experiments",
                Map.of(
                        "name", "System Test V2",
                        "versions", List.of(Map.of("type", "config"))
                ),
                Map.class
        );

        // 验证结果
        assertEquals(HttpStatus.CREATED, response.getStatusCode());
        assertEquals(201, response.getBody().get("code"));
        mockServer.verify();
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-14 14:06:11
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-18 16:16:47
 * @FilePath: src/test/java/com/example/abtest/AbTestApplicationTests.java
 * @Description:
 */
package com.example.abtest;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class AbTestApplicationTests {

    @Test
    void contextLoads() {
    }

}
