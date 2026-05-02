import 'package:flutter/material.dart';

import 'dashboard_screen.dart';

/// Demographic data form. Filled in commit 13.
class ProfileFormScreen extends StatelessWidget {
  final bool skipIfFilled;
  const ProfileFormScreen({super.key, this.skipIfFilled = false});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Datos demográficos')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Form coming in next commit (13).'),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const DashboardScreen()),
                ),
                child: const Text('Continuar al monitor'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
