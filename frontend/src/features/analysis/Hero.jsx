import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Search, Activity, Database } from 'lucide-react';

const Hero = ({ onStart }) => {
  const features = [
    { icon: Activity, title: 'Acoustic Anomaly', desc: 'Deep analysis of spectral artifacts and pitch instability.' },
    { icon: Search, title: 'Visual XAI', desc: 'Grad-CAM and Integrated Gradients for neural focus mapping.' },
    { icon: Zap, title: 'Real-time Inference', desc: 'Hybrid model fusion for rapid forensic classification.' },
    { icon: Database, title: 'Audit Persistence', desc: 'Secure storage and versioning of all forensic investigations.' },
  ];

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mb-8"
      >
        <div className="w-20 h-20 bg-primary/20 rounded-3xl flex items-center justify-center mb-6 mx-auto">
          <Shield className="text-primary" size={40} />
        </div>
        <h1 className="text-4xl font-semibold mb-4 tracking-tight">
          Advanced <span className="text-gradient">Forensic Audio</span> Analysis
        </h1>
        <p className="text-base text-muted max-w-xl mx-auto mb-10 leading-relaxed">
          Verify authenticity with state-of-the-art deepfake detection and 
          explainable AI indicators. Trusted for professional forensic audits.
        </p>
        
        <div className="flex gap-4 justify-center">
          <button onClick={onStart} className="btn btn-primary px-8 py-3">
            Start Investigation
          </button>
          <button className="btn btn-ghost px-8 py-3">
            System Methodology
          </button>
        </div>
      </motion.div>

      <div className="grid-container w-full mt-20">
        {features.map((f, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            className="span-3 glass glass-hover p-6 text-left"
          >
            <f.icon className="text-primary mb-4" size={24} />
            <h3 className="text-base mb-2">{f.title}</h3>
            <p className="text-xs text-muted leading-relaxed">{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Hero;
