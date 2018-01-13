package com.su.androidblog.request;

import android.content.Context;

import com.android.volley.Request.Method;
import com.android.volley.Response.ErrorListener;
import com.android.volley.Response.Listener;
import com.su.androidblog.bean.Blogs;
import com.su.androidblog.bean.BlogsHead;
import com.su.androidblog.util.NetConfig;

public class ApiRequests {

    private static ApiRequests mInstance;

    public static ApiRequests getInstance() {
        if (mInstance == null) {
            mInstance = new ApiRequests();
        }
        return mInstance;
    }

    public void getBlogs(Context context, Listener<?> listener, ErrorListener errorListener) {
        String url = NetConfig.URL_BLOG_LIST;

        GsonRequest<BlogsHead> request = new GsonRequest<BlogsHead>(Method.GET, url, BlogsHead.class, (Listener<BlogsHead>) listener, errorListener);
        RequestManager.getRequestQueue().add(request);
    }
}
