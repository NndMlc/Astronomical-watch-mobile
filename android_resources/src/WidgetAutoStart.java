package org.astronomicalwatch.astronomical_watch;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import org.kivy.android.PythonService;

/**
 * Starts widget service automatically when:
 * 1. Widget is added to home screen
 * 2. Device boots up
 * 3. App is installed
 */
public class WidgetAutoStart extends BroadcastReceiver {
    
    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        
        if (action != null) {
            switch (action) {
                case "android.appwidget.action.APPWIDGET_ENABLED":
                case "android.intent.action.BOOT_COMPLETED":
                case "android.intent.action.MY_PACKAGE_REPLACED":
                    startWidgetService(context);
                    break;
            }
        }
    }
    
    private void startWidgetService(Context context) {
        Intent serviceIntent = new Intent(context, PythonService.class);
        serviceIntent.putExtra("serviceEntrypoint", "service/widget_service.py");
        serviceIntent.putExtra("serviceTitle", "Astronomical Watch");
        serviceIntent.putExtra("serviceDescription", "Updates astronomical time widget");
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(serviceIntent);
        } else {
            context.startService(serviceIntent);
        }
    }
}
