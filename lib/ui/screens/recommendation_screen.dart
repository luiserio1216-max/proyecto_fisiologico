import 'package:flutter/material.dart';

/// Filled in commit 14.
class RecommendationScreen extends StatelessWidget {
  const RecommendationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recomendación')),
      body: const Center(
        child: Text('Recommendation engine UI coming in next commit (14).'),
      ),
    );
  }
}
