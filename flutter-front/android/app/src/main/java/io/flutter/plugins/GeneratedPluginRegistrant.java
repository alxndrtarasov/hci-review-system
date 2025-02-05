package io.flutter.plugins;

import io.flutter.plugin.common.PluginRegistry;
import com.ly.permission.PermissionPlugin;
import bz.rxla.flutter.speechrecognition.SpeechRecognitionPlugin;
import com.blounty.tts.TtsPlugin;

/**
 * Generated file. Do not edit.
 */
public final class GeneratedPluginRegistrant {
  public static void registerWith(PluginRegistry registry) {
    if (alreadyRegisteredWith(registry)) {
      return;
    }
    PermissionPlugin.registerWith(registry.registrarFor("com.ly.permission.PermissionPlugin"));
    SpeechRecognitionPlugin.registerWith(registry.registrarFor("bz.rxla.flutter.speechrecognition.SpeechRecognitionPlugin"));
    TtsPlugin.registerWith(registry.registrarFor("com.blounty.tts.TtsPlugin"));
  }

  private static boolean alreadyRegisteredWith(PluginRegistry registry) {
    final String key = GeneratedPluginRegistrant.class.getCanonicalName();
    if (registry.hasPlugin(key)) {
      return true;
    }
    registry.registrarFor(key);
    return false;
  }
}
