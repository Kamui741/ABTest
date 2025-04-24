/*
 * @Author: ChZheng
 * @Date: 2025-04-18 16:30:40
 * @LastEditTime: 2025-04-25 01:34:07
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: /code/ABTest/ABTestProxy/IUserService.java
 */


 package com.citicbank.chdp.api.userInterface;
 import com.citicbank.api.exception.BussinessException;
 import reactor.core.publisher.Mono;

 public interface IUserService {
     Mono<User> createUser(User user) throws  BusinessException;
 }
/*
 * @Author: ChZheng
 * @Date: 2025-04-18 16:37:10
 * @LastEditTime: 2025-04-18 16:45:48
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: /springboot-one-hop/api/src/main/java/org/com/citicbank/chdp/api/userInterface/User.java
 */
import javax.validation.constraints.*;
import java.io.Serializable;
import java.math.BigDecimal;
public class User  implements Serializable {
    private static final long serialVersionUID = 1L;

    @NotNull(message = "用户名不能为空")
    private Long id;

    @NotNull(message = "用户名不能为空")
    @Size(min = 2, max = 10, message = "用户名长度必须在2到10之间")
    private String name;

    @Digits(integer = 3, fraction = 0, message = "年龄必须是整数")
    private Integer age;

    @Digits(integer = 10, fraction = 2, message = "工资必须是整数")
    private BigDecimal money;

    @Pattern(regexp = "['男'｜'女']", message = "性别必须是男或女")
    @Size(max = 1)
    private String sex;

    @Pattern(regexp = "\\d{11}", message = "手机号必须是11位数字")
    @Size(max = 11)
    private String mobile;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;

    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public BigDecimal getMoney() {
        return money;
    }

    public void setMoney(BigDecimal money) {
        this.money = money;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getMobile() {
        return mobile;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", age=" + age +
                ", money=" + money +
                ", sex='" + sex + '\'' +
                ", mobile='" + mobile + '\'' +
                '}';
    }
}
/**
 * @Author: ChZheng
 * @Date: 2025-04-18 16:52:40
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-21 09:22:58
 * @FilePath: test-client/src/main/java/com/citicbank/ncim/controller/TestController.java
 * @Description:
 */
package main.java.com.citicbank.ncim.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;

import com.citicbank.api.exception.BusinessException;
import com.citicbank.api.exception.EBusinessException;
import com.citicbank.api.exception.SystemException;
import com.citicbank.chdp.api.userInterface.IUserService;


import com.citicbank.chdp.api.userInterface.User;

import com.citicbank.crpc.common.constants.ConfigKey;
import com.citicbank.crpc.common.entity.RpcContext;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import java.math.BigDecimal;

@Slf4j
@Controller
@RequestMapping("/api/client")
public class TestController {
    @CrpcReference(registry = "chdp",timeout = 30000,methods={@CrpcMethod(name="createUser",timeout=30000)})
    IUserService userService;

    @ResponseBody
    @RequestMapping(value = "/geguser", method = RequestMethod.GET)
    public User getUser() {
        User userresult = null;
        try {
            RpcContext.getRpcContext()
                    .setConfig(ConfigKey.intorSystCod,"NCIM")
                    .setConfig(ConfigKey.sendSystCod,"CBPD")
                    .setConfig(ConfigKey.intorTranjnalNum,"NCIM21342235267586")
                    .setConfig(ConfigKey.aplySystTmtp,"2020-04-18 16:52:40")
                    .setConfig(ConfigKey.bankNum,"001")
                    .setConfig(ConfigKey.sendSystTmtp,"2020-04-18 16:52:40")
                    .setConfig(ConfigKey.sendTranjnalNum,"CBPD21342235267586");
            org.springframework.boot.autoconfigure.security.SecurityProperties.User user = new User();
            user.setSex("男");
            user.setName("null");
            user.setId("123");
            user.setAge("123")
            user.setMobile("123");
            BigDecimal bigDecimal = new BigDecimal("123");
            user.setMoney(bigDecimal);
            Mono<User> userMono = userService.createUser(user);
            userresult = userMono.block();
        }catch (Throwable throwable){
            dealException(throwable);
        }
        return userresult;
    }

    private void dealException(Throwable throwable) {
        Throwable throwableReal = Exception.unwrap(throwable);
        log.error("调用接口异常", throwableReal);
        if (throwableReal instanceof RpcException) {
            RpcException re = (RpcException) throwableReal;
            RpcErrorLevel errorLevel = RpcExceptionUtils.getErrorLevel(re.getCode());
            if (errorLevel == RpcErrorLevel.FAILED) {
            } else if (errorLevel == RpcErrorLevel.UNKNOWEN) {

            }
        }
        else if (throwableReal instanceof EBusinessException||throwableReal instanceof BusinessException||throwableReal instanceof SystemException) {
            //业务异常
        } else {

        }
    }


}
/*
 * @Author: ChZheng
 * @Date: 2025-04-18 17:15:17
 * @LastEditTime: 2025-04-18 17:15:17
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: /springboot-one-hop/test-client/src/main/java/com/citicbank/ncim/ClientApplication.java
 */
@SpringBootApplication
@EnableCrpc(scanBasePackages = "com.citicbank.com")
public class ClientApplication {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(ClientApplication.class);
        app.run(args);
    }
}
server.port=8081

app.name=NCIM
crpc.client.sendSystCod=NCIM
crpc.registry.id = chdp
crpc.registry.protocol=crpc
crpc.registry.address=127.0.0.1:2181

service.port = 8081
crpc.registry.id = chdp
crpc.registry.protocol = crpc
crpc.registry.address = 127.0.0.1:2181
app.name = CDHP


/*
 * @Author: ChZheng
 * @Date: 2025-04-18 17:22:52
 * @LastEditTime: 2025-04-21 09:22:58
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: test-service/src/main/java/com/citicbank/chdp/api/userImpl/UserServiceImpl.java
 */
public class UserServiceImpl implements IUserService {
    if(user.getId()==111)
    {
        throw new BusinessException("用户不存在");
    }
    return Mono.just(user);
}
package main.java.com.citicbank.chdp.api;

/**
 * @Author: ChZheng
 * @Date: 2025-04-18 17:22:22
 * @LastEditors: ChZheng
 * @LastEditTime: 2025-04-21 09:22:58
 * @FilePath: test-service/src/main/java/com/citicbank/chdp/api/ServerApplication.java
 * @Description:
 */

public class ServerApplication {

}
