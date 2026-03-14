
//learn more scroll

import React from 'react';
import { Button } from './ui/button';
import { ArrowRight, Shield, Cpu, Database } from 'lucide-react';

export default function HeroSection({ onNavigate, onGetStarted }) {
  return (
    <section
      id="home"
      className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 flex items-center"
    >
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="space-y-6">
              <div className="inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-sm font-medium">
                <Cpu className="w-4 h-4 mr-2" />
                AI-Powered Cryptographic Analysis
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-gray-900 via-blue-900 to-cyan-700 bg-clip-text text-transparent">
                  Decode the Future
                </span>
                <br />
                <span className="text-gray-800">
                  of Cryptography
                </span>
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed max-w-xl">
                Our cutting-edge AI analyzes encrypted data to reveal the
                cryptographic algorithm behind it—whether classical or
                post-quantum. Every discovery is sealed on a blockchain,
                ensuring transparency, trust, and tamper-proof security.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white px-8 py-3 shadow-xl"
                onClick={onGetStarted}
              >
                Get Started
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>

              <Button
                size="lg"
                variant="outline"
                className="border-gray-300 text-gray-700 hover:bg-gray-50 px-8 py-3"
                onClick={() => onNavigate && onNavigate('faq')}
              >
                Learn More
              </Button>
            </div>

            <div className="flex items-center gap-8 pt-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">20+</div>
                <div className="text-sm text-gray-600">Algorithms Detected</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">80%</div>
                <div className="text-sm text-gray-600">Accuracy Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">24/7</div>
                <div className="text-sm text-gray-600">Blockchain Security</div>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-3xl blur-3xl opacity-20 animate-pulse"></div>
            <div className="relative bg-white p-8 rounded-3xl shadow-2xl border border-gray-200">
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-6">
                  <Shield className="w-6 h-6 text-blue-600" />
                  <span className="font-semibold text-gray-900">
                    Live Analysis Dashboard
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-xl">
                    <div>
                      <div className="font-medium text-green-900">RSA-2048</div>
                      <div className="text-sm text-green-700">
                        Classical Algorithm
                      </div>
                    </div>
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-xl">
                    <div>
                      <div className="font-medium text-blue-900">Kyber-768</div>
                      <div className="text-sm text-blue-700">Post-Quantum</div>
                    </div>
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-purple-50 border border-purple-200 rounded-xl">
                    <div>
                      <div className="font-medium text-purple-900">
                        ECDSA-P256
                      </div>
                      <div className="text-sm text-purple-700">
                        Elliptic Curve
                      </div>
                    </div>
                    <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
                  </div>
                </div>
                <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                  <Database className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600">
                    Secured on blockchain
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
