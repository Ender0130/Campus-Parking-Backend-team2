import { LogBox } from "react-native";
import { Stack } from "expo-router";

LogBox.ignoreLogs(["Snapshotting a view"]);

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="home" options={{ headerShown: false }} />
    </Stack>
  );
}
