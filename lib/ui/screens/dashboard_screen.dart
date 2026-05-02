import 'package:flutter/material.dart';

/// Live ECG dashboard. Filled in commit 12.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Monitor en vivo')),
      body: const Center(
        child: Text('Live ECG chart + BPM coming in next commit (12).'),
      ),
    );
  }
}
