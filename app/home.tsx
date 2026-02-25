import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, TouchableOpacity, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getLots, submitReport } from '../services/api';
import { useLocalSearchParams } from 'expo-router';

interface Lot {
  name: string;
  status: string;
  color: string;
  last_updated: string;
  total_spots: number;
}

export default function Home() {
  const { campus, residential } = useLocalSearchParams();
  const [lots, setLots] = useState<Lot[]>([]);

  useEffect(() => {
    const loadLots = async () => {
      const data = await getLots();
      setLots(data);
    };
    loadLots();
  }, []);

  const handleReport = async (lotName: string, status: string) => {
    try {
      await submitReport(lotName, status, 'guest'); // replace 'guest' later
      Alert.alert('Success', `Reported ${status} for ${lotName}`);
      const updated = await getLots();
      setLots(updated);
    } catch (err) {
      Alert.alert('Error', 'Report failed');
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <Text style={styles.title}>Parking Lots at {campus || 'Campus'}</Text>
        {lots.length === 0 ? (
          <>
            <Text style={styles.emoji}>🚧</Text>
            <Text style={styles.title}>Work In Progress</Text>
            <Text style={styles.subtitle}>No lots available yet or loading...</Text>
          </>
        ) : (
          <FlatList
            data={lots}
            keyExtractor={item => item.name}
            renderItem={({ item }) => (
  <View style={styles.card}>
    <View style={[styles.colorBar, { backgroundColor: item.color }]} />
    <Text style={styles.name}>{item.name}</Text>
    <Text>Status: {item.status}</Text>
    <Text>Last updated: {new Date(item.last_updated).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZone: 'America/Los_Angeles' //San Diego time (auto handles PST/PDT)
    })} PST</Text>
    <View style={styles.buttonsRow}>
      <TouchableOpacity style={styles.btn} onPress={() => handleReport(item.name, 'AVAILABLE')}>
        <Text>AVAILABLE</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.btn} onPress={() => handleReport(item.name, 'LIMITED')}>
        <Text>LIMITED</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.btn} onPress={() => handleReport(item.name, 'FULL')}>
        <Text>FULL</Text>
      </TouchableOpacity>
    </View>
  </View>
   )}
    />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#fff" },
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 16, color: "#1a1a2e" },
  subtitle: { fontSize: 16, color: "#888", textAlign: "center" },
  emoji: { fontSize: 52, marginBottom: 8 },
  card: { backgroundColor: "#fff", padding: 16, marginBottom: 12, borderRadius: 12 },
  colorBar: { height: 10, borderRadius: 5, marginBottom: 8 },
  name: { fontSize: 18, fontWeight: "bold" },
  buttonsRow: { flexDirection: "row", justifyContent: "space-around", marginTop: 12 },
  btn: { backgroundColor: "#007AFF", padding: 10, borderRadius: 8, flex: 1, marginHorizontal: 4, alignItems: "center" },
});