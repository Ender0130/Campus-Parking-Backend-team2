import {
  Poppins_400Regular,
  Poppins_500Medium,
  Poppins_600SemiBold,
  Poppins_700Bold,
  Poppins_900Black,
  useFonts,
} from "@expo-google-fonts/poppins";
import { useEffect, useRef, useState } from "react";
import {
  Animated,
  Easing,
  FlatList,
  ImageBackground,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

const PRIMARY = "#4F46E5";

const CAMPUSES = ["SDSU"];
const CAMPUS_LABELS: Record<string, string> = {
  SDSU: "SDSU - San Diego State University",
};

const COMMUNITIES = [
  "Aztec Corner",
  "Aztec Shores",
  "Chapultepec Hall",
  "Cuicacalli Suites",
  "Diegueno Hall",
  "Olmeca Hall",
  "South Campus Plaza",
  "Tenochca Hall",
  "Tepeyac Hall",
  "Villa Alvarado",
  "Zura Hall",
];

type DropdownProps = {
  placeholder: string;
  options: string[];
  selected: string;
  onSelect: (value: string) => void;
  getLabel?: (value: string) => string;
};

function Dropdown({ placeholder, options, selected, onSelect, getLabel }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const backdropAnim = useRef(new Animated.Value(0)).current;
  const sheetAnim = useRef(new Animated.Value(300)).current;

  useEffect(() => {
    if (open) {
      Animated.parallel([
        Animated.timing(backdropAnim, {
          toValue: 1,
          duration: 420,
          easing: Easing.out(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(sheetAnim, {
          toValue: 0,
          duration: 480,
          easing: Easing.out(Easing.cubic),
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(backdropAnim, {
          toValue: 0,
          duration: 320,
          easing: Easing.in(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(sheetAnim, {
          toValue: 300,
          duration: 320,
          easing: Easing.in(Easing.cubic),
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [open]);

  return (
    <>
      <TouchableOpacity
        style={styles.dropdown}
        onPress={() => setOpen(true)}
        activeOpacity={0.7}
      >
        <Text style={selected ? styles.dropdownText : styles.dropdownPlaceholder}>
          {selected || placeholder}
        </Text>
        <Text style={styles.chevron}>▾</Text>
      </TouchableOpacity>

      <Modal
        visible={open}
        transparent
        animationType="none"
        onRequestClose={() => setOpen(false)}
      >
        <TouchableOpacity
          style={styles.overlay}
          activeOpacity={1}
          onPress={() => setOpen(false)}
        >
          <Animated.View style={[StyleSheet.absoluteFill, styles.backdrop, { opacity: backdropAnim }]} />
          <Animated.View style={[styles.sheet, { transform: [{ translateY: sheetAnim }] }]}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>{placeholder}</Text>
            <FlatList
              data={options}
              keyExtractor={(item) => item}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={styles.sheetItem}
                  onPress={() => {
                    onSelect(item);
                    setOpen(false);
                  }}
                >
                  <Text
                    style={[
                      styles.sheetItemText,
                      item === selected && styles.sheetItemTextSelected,
                    ]}
                  >
                    {getLabel ? getLabel(item) : item}
                  </Text>
                  {item === selected && <Text style={styles.checkmark}>✓</Text>}
                </TouchableOpacity>
              )}
            />
          </Animated.View>
        </TouchableOpacity>
      </Modal>
    </>
  );
}

export default function Index() {
  const [fontsLoaded] = useFonts({
    Poppins_400Regular,
    Poppins_500Medium,
    Poppins_600SemiBold,
    Poppins_700Bold,
    Poppins_900Black,
  });

  const router = useRouter();
  const [campus, setCampus] = useState("");
  const [community, setCommunity] = useState("");

  if (!fontsLoaded) return null;

  return (
    <ImageBackground
      source={require("../assets/images/background.png")}
      style={styles.root}
      imageStyle={styles.backgroundImage}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.safe}>

        {/* Header */}
        <View style={styles.header}>
          <View style={styles.titleRow}>
            <Text style={styles.appName}>Campus</Text>
            <Text style={styles.appNameAccent}>Park</Text>
          </View>
          <Text style={styles.tagline}>Find your spot. Park smart.</Text>
        </View>

        {/* Middle — dropdowns centered */}
        <View style={styles.middle}>
          <Text style={styles.fieldLabel}>Campus</Text>
          <Dropdown
            placeholder="Select your campus"
            options={CAMPUSES}
            selected={campus}
            onSelect={setCampus}
            getLabel={(v) => CAMPUS_LABELS[v] ?? v}
          />

          <View style={styles.fieldGap} />

          <Text style={styles.fieldLabel}>Residential community</Text>
          <Dropdown
            placeholder="Where do you live?"
            options={COMMUNITIES}
            selected={community}
            onSelect={setCommunity}
          />
        </View>

        {/* Bottom — login button */}
        <View style={styles.bottom}>
          <TouchableOpacity
            style={[
              styles.loginBtn,
              (!campus || !community) && styles.loginBtnDisabled,
            ]}
            activeOpacity={0.85}
            disabled={!campus || !community}
            onPress={() => router.push("/home")}
          >
            <Text style={styles.loginBtnText}>Log in</Text>
          </TouchableOpacity>
        </View>

      </SafeAreaView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  backgroundImage: { opacity: 0.75 },
  safe: { flex: 1 },

  // ── Header ──────────────────────────────────────────
  header: {
    paddingHorizontal: 28,
    paddingTop: 12,
    alignItems: "center",
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 2,
  },
  appName: {
    fontFamily: "Poppins_900Black",
    fontSize: 44,
    color: "#fff",
    letterSpacing: -1,
  },
  appNameAccent: {
    fontFamily: "Poppins_900Black",
    fontSize: 44,
    color: PRIMARY,
    letterSpacing: -1,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: "#FFB703",
    marginLeft: 5,
    alignSelf: "center",
    marginTop: 6,
  },
  tagline: {
    fontFamily: "Poppins_400Regular",
    fontSize: 14,
    color: "rgba(255,255,255,0.95)",
    marginTop: -4,
    textAlign: "center",
  },

  // ── Middle ───────────────────────────────────────────
  middle: {
    flex: 1,
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  fieldLabel: {
    fontFamily: "Poppins_600SemiBold",
    fontSize: 11,
    color: PRIMARY,
    letterSpacing: 1.2,
    textTransform: "uppercase",
    marginBottom: 8,
    textAlign: "center",
  },
  fieldGap: { height: 20 },

  // ── Glass dropdown ───────────────────────────────────
  dropdown: {
    backgroundColor: "rgba(255,255,255,0.32)",
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: "rgba(255,255,255,0.7)",
    paddingVertical: 16,
    paddingHorizontal: 18,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    shadowColor: "#000",
    shadowOpacity: 0.18,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  dropdownText: {
    fontFamily: "Poppins_600SemiBold",
    fontSize: 15,
    color: PRIMARY,
    flex: 1,
  },
  dropdownPlaceholder: {
    fontFamily: "Poppins_400Regular",
    fontSize: 15,
    color: "rgba(20,10,60,0.65)",
    flex: 1,
  },
  chevron: {
    fontSize: 18,
    color: "rgba(20,10,60,0.65)",
    marginLeft: 8,
  },

  // ── Bottom ───────────────────────────────────────────
  bottom: {
    paddingHorizontal: 24,
    paddingBottom: 44,
  },
  loginBtn: {
    backgroundColor: PRIMARY,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: "center",
    shadowColor: PRIMARY,
    shadowOpacity: 0.45,
    shadowRadius: 14,
    shadowOffset: { width: 0, height: 4 },
    elevation: 8,
  },
  loginBtnDisabled: {
    backgroundColor: "#3730a3",
    shadowOpacity: 0,
    elevation: 0,
  },
  loginBtnText: {
    fontFamily: "Poppins_700Bold",
    color: "#fff",
    fontSize: 17,
    letterSpacing: 0.3,
  },

  // ── Bottom sheet (modal) ──────────────────────────────
  overlay: {
    flex: 1,
    justifyContent: "flex-end",
  },
  backdrop: {
    backgroundColor: "rgba(0,0,0,0.4)",
  },
  sheet: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    padding: 20,
    paddingBottom: 40,
    maxHeight: "65%",
  },
  sheetHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: "#E0E0E0",
    alignSelf: "center",
    marginBottom: 16,
  },
  sheetTitle: {
    fontFamily: "Poppins_600SemiBold",
    fontSize: 11,
    color: "#AEAEB2",
    letterSpacing: 1,
    textTransform: "uppercase",
    marginBottom: 8,
    paddingHorizontal: 8,
  },
  sheetItem: {
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#F2F2F7",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sheetItemText: {
    fontFamily: "Poppins_400Regular",
    fontSize: 16,
    color: "#1a1a2e",
  },
  sheetItemTextSelected: {
    fontFamily: "Poppins_600SemiBold",
    color: PRIMARY,
  },
  checkmark: {
    color: PRIMARY,
    fontSize: 16,
    fontFamily: "Poppins_700Bold",
  },
});
