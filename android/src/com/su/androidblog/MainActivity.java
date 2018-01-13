package com.su.androidblog;

import java.util.ArrayList;
import java.util.List;

import com.android.volley.Response;
import com.android.volley.Response.Listener;
import com.android.volley.VolleyError;
import com.su.androidblog.adapter.CustomAdapter;
import com.su.androidblog.bean.Blogs;
import com.su.androidblog.bean.BlogsHead;
import com.su.androidblog.request.ApiRequests;
import com.su.androidblog.request.RequestManager;

import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ListView;
import android.widget.TextView;

public class MainActivity extends Activity implements CustomAdapter.LayoutView {

    private final static int UPDATE_UI = 0;

    private static final String TAG = MainActivity.class.getSimpleName();

    List<Blogs> mBlogs;
    private Context mContext;
    private CustomAdapter<Blogs> mCustomAdapter;

    private ListView mListView;

    private Handler mHandler = new Handler() {

        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
            case UPDATE_UI:
                mCustomAdapter.updateData((ArrayList<Blogs>) mBlogs);
                break;

            default:
                break;
            }

        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initView();
        initValue();
        initListener();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateBlogs();
    }

    private void initView() {
        mListView = (ListView) findViewById(R.id.listView);
    }

    private void initValue() {
        mContext = this;
        mBlogs = new ArrayList<Blogs>();

        mCustomAdapter = new CustomAdapter<Blogs>(mBlogs);

        mCustomAdapter.setLayoutView(this);
        mListView.setAdapter(mCustomAdapter);

        // 初始化网络
        RequestManager.init(this);
    }

    private void initListener() {

    }

    public void updateBlogs() {
        Log.d(TAG, "updateBlogs");

        ApiRequests.getInstance().getBlogs(mContext, new Listener<BlogsHead>() {

            @Override
            public void onResponse(BlogsHead response) {
                mBlogs.clear();
                mBlogs = response.blogs;
                mHandler.sendEmptyMessage(UPDATE_UI);
            }

        }, new Response.ErrorListener() {

            @Override
            public void onErrorResponse(VolleyError error) {
                Log.d(TAG, error.toString());
            }

        });
    }

    class ViewHolder {
        TextView tv_title;
        TextView tv_content;
    }

    @Override
    public <T> View setView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;

        if (convertView == null) {
            convertView = LayoutInflater.from(mContext).inflate(R.layout.item_blog_list, null);

            holder = new ViewHolder();
            holder.tv_title = (TextView) convertView.findViewById(R.id.tv_title);
            holder.tv_content = (TextView) convertView.findViewById(R.id.tv_content);

            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        Blogs mBlog = mBlogs.get(position);

        holder.tv_title.setText(mBlog.name);
        holder.tv_content.setText(mBlog.summary);

        return convertView;
    }

}
