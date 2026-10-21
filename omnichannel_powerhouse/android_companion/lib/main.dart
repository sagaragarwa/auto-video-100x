import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const OmniChannelApp());
}

class OmniChannelApp extends StatelessWidget {
  const OmniChannelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OmniChannel Studio',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF080C14),
        primaryColor: const Color(0xFF06B6D4),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF06B6D4),
          secondary: Color(0xFF10B981),
          surface: Color(0xFF111827),
        ),
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;
  String _serverUrl = "http://10.0.2.2:8899"; // Default Android emulator address to host PC
  String _convoId = "6a60d582-ca94-43f1-bef4-cbc8f38f0265";
  
  Map<String, dynamic> _systemStatus = {};
  List<dynamic> _channels = [];
  bool _isLoading = false;

  final TextEditingController _themeController = TextEditingController(
    text: "Frontier AI Hardware Monopolies & Wall Street High-Frequency Trading Warfare",
  );
  final TextEditingController _serverController = TextEditingController();
  final TextEditingController _convoController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _serverUrl = prefs.getString('server_url') ?? "http://10.0.2.2:8899";
      _convoId = prefs.getString('convo_id') ?? "6a60d582-ca94-43f1-bef4-cbc8f38f0265";
      _serverController.text = _serverUrl;
      _convoController.text = _convoId;
    });
    _fetchTelemetry();
  }

  Future<void> _savePreferences() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_url', _serverController.text.trim());
    await prefs.setString('convo_id', _convoController.text.trim());
    setState(() {
      _serverUrl = _serverController.text.trim();
      _convoId = _convoController.text.trim();
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Settings and Conversation ID Saved!")),
    );
    _fetchTelemetry();
  }

  Future<void> _fetchTelemetry() async {
    setState(() => _isLoading = true);
    try {
      final statusRes = await http.get(Uri.parse("$_serverUrl/api/status")).timeout(const Duration(seconds: 4));
      if (statusRes.statusCode == 200) {
        _systemStatus = jsonDecode(statusRes.body);
      }

      final chRes = await http.get(Uri.parse("$_serverUrl/api/channels")).timeout(const Duration(seconds: 4));
      if (chRes.statusCode == 200) {
        _channels = jsonDecode(chRes.body)['channels'] ?? [];
      }
    } catch (e) {
      debugPrint("Telemetry fetch error: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _launch20VideoCampaign() async {
    setState(() => _isLoading = true);
    try {
      final res = await http.post(
        Uri.parse("$_serverUrl/api/dispatch"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"theme": _themeController.text.trim()}),
      );

      final data = jsonDecode(res.body);
      if (data['success'] == true) {
        _showDialog("Swarm Launched!", "20 Parallel Cloud Runners are now active on GitHub Actions! Direct publishing to YouTube & Rumble is underway.");
      } else {
        _showDialog("Dispatch Notice", data['message'] ?? "Unknown response");
      }
    } catch (e) {
      _showDialog("Connection Error", "Could not reach PC server at $_serverUrl: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF111827),
        title: Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Text(content, style: const TextStyle(color: Colors.white70)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("OK", style: TextStyle(color: Color(0xFF06B6D4))),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF111827),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF06B6D4), Color(0xFF10B981)]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text("Ω", style: TextStyle(color: Colors.black, fontWeight: FontWeight.w900)),
            ),
            const SizedBox(width: 10),
            const Text("OmniChannel", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF06B6D4)),
            onPressed: _fetchTelemetry,
          ),
        ],
      ),
      body: _isLoading && _systemStatus.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : IndexedStack(
              index: _currentIndex,
              children: [
                _buildFlightDeckTab(),
                _buildLaunchCampaignTab(),
                _buildChannelsTab(),
                _buildSettingsTab(),
              ],
            ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        backgroundColor: const Color(0xFF111827),
        selectedItemColor: const Color(0xFF06B6D4),
        unselectedItemColor: Colors.white38,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.radar), label: "Radar"),
          BottomNavigationBarItem(icon: Icon(Icons.rocket_launch), label: "Dispatch"),
          BottomNavigationBarItem(icon: Icon(Icons.tv), label: "Fleet"),
          BottomNavigationBarItem(icon: Icon(Icons.sync_alt), label: "Bridge"),
        ],
      ),
    );
  }

  Widget _buildFlightDeckTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Conversation ID Bridge Header
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF111827),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.link, color: Color(0xFF10B981), size: 18),
                  SizedBox(width: 8),
                  Text("ACTIVE CONVERSATION BRIDGE", style: TextStyle(color: Color(0xFF10B981), fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
              const SizedBox(height: 6),
              Text(_convoId, style: const TextStyle(color: Colors.white, fontSize: 13, fontFamily: "monospace")),
              const SizedBox(height: 4),
              const Text("Synced with Windows Antigravity Brain", style: TextStyle(color: Colors.white38, fontSize: 11)),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // KPIs Grid
        Row(
          children: [
            Expanded(
              child: _buildMetricCard("TOKEN SAVINGS", "500x", "400 tokens = 20 vids", const Color(0xFF06B6D4)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard("OUTRO LOCK", "100%", "Signature Clip Locked", const Color(0xFF10B981)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard("CHANNELS", "${_systemStatus['total_channels'] ?? 2}", "YouTube + Rumble", Colors.amber),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard("CLOUD RUNNERS", "20 Parallel", "GitHub Actions 24/7", Colors.purpleAccent),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(String label, String value, String sub, Color accent) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111827),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Colors.white38, fontSize: 10, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(value, style: TextStyle(color: accent, fontSize: 22, fontWeight: FontWeight.w900)),
          const SizedBox(height: 4),
          Text(sub, style: const TextStyle(color: Colors.white54, fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildLaunchCampaignTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("Ignite 20-Video Swarm", style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text("Triggers 20 parallel cloud runners with zero token burn.", style: TextStyle(color: Colors.white54, fontSize: 12)),
        const SizedBox(height: 20),
        TextField(
          controller: _themeController,
          maxLines: 4,
          style: const TextStyle(color: Colors.white, fontSize: 14),
          decoration: InputDecoration(
            labelText: "Master Campaign Theme",
            labelStyle: const TextStyle(color: Color(0xFF06B6D4)),
            filled: true,
            fillColor: const Color(0xFF111827),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: _launch20VideoCampaign,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF10B981),
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          child: const Text("🚀 LAUNCH 20-VIDEO CLOUD SWARM", style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 14)),
        ),
      ],
    );
  }

  Widget _buildChannelsTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _channels.length,
      itemBuilder: (context, idx) {
        final ch = _channels[idx];
        final quota = ch['quota_status'] ?? {};
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF111827),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.08)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(ch['name'] ?? 'Channel', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: (ch['platform'] == 'youtube' ? Colors.red : Colors.green).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(ch['platform']?.toUpperCase() ?? 'YT', style: TextStyle(color: ch['platform'] == 'youtube' ? Colors.redAccent : Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text("${ch['handle'] ?? ch['channel_id']} · ${ch['niche']}", style: const TextStyle(color: Color(0xFF06B6D4), fontSize: 12)),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("Today's Quota", style: TextStyle(color: Colors.white54, fontSize: 12)),
                  Text("${quota['current_daily_count'] ?? 0} / ${quota['max_allowed'] ?? 3} uploads", style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSettingsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("Remote Bridge & Connection", style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        TextField(
          controller: _serverController,
          style: const TextStyle(color: Colors.white, fontSize: 13),
          decoration: InputDecoration(
            labelText: "Studio Dashboard Server URL",
            hintText: "http://192.168.1.5:8899 or tunnel URL",
            filled: true,
            fillColor: const Color(0xFF111827),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _convoController,
          style: const TextStyle(color: Colors.cyanAccent, fontSize: 13, fontFamily: "monospace"),
          decoration: InputDecoration(
            labelText: "Antigravity Conversation ID",
            hintText: "6a60d582-ca94-43f1-bef4-cbc8f38f0265",
            filled: true,
            fillColor: const Color(0xFF111827),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: _savePreferences,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF06B6D4),
            padding: const EdgeInsets.symmetric(vertical: 14),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          child: const Text("Save & Connect", style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}
