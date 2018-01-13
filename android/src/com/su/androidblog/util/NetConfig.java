package com.su.androidblog.util;

public class NetConfig {

    /**
     * 因为http://127.0.0.1:9000/ 访问PC本地机启动的服务器时会报错, 因为android会默认访问它本身 故使用
     * http://10.0.2.2:9000/
     */
    public static final String HOST_LAVA_POWERSAVE = "http://10.0.2.2:9000";

    public static final String URL_BLOG_LIST = HOST_LAVA_POWERSAVE + "/api/blogs/all";

}
