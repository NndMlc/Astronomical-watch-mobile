package org.astronomicalwatch.astronomical_watch;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;
import android.app.PendingIntent;
import android.os.Build;
import org.kivy.android.PythonService;

/**
 * Android Home Screen Widget Provider for Astronomical Watch
 * Displays Dies.miliDies on home screen, opens app on tap
 */
public class AstroWidgetProvider extends AppWidgetProvider {
    
    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        // Widget update is handled by Python code via Pyjnius
        // This is just the entry point that Android calls
        
        for (int appWidgetId : appWidgetIds) {
            RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_layout);
            
            // Set default text
            views.setTextViewText(R.id.widget_time, "---");
            
            // Create intent to launch main activity
            Intent intent = new Intent(context, org.kivy.android.PythonActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            PendingIntent pendingIntent = PendingIntent.getActivity(
                context, 0, intent, 
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            );
            
            views.setOnClickPendingIntent(R.id.widget_layout, pendingIntent);
            
            // Update widget
            appWidgetManager.updateAppWidget(appWidgetId, views);
        }
    }
    
    @Override
    public void onEnabled(Context context) {
        // First widget added - start background service
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
    
    @Override
    public void onDisabled(Context context) {
        // Last widget removed - stop service
        Intent serviceIntent = new Intent(context, PythonService.class);
        context.stopService(serviceIntent);
    }
}
