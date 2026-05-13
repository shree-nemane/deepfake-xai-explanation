import React from 'react';
import { motion } from 'framer-motion';
import { Maximize2, Info } from 'lucide-react';

const VisualXAI = ({ gradcam, ig }) => {
  return (
    <div className="grid-container">
      <div className="span-6 glass p-6">
        <div className="flex flex-col justify-between items-center mb-6">
          <h3 className="text-md mb-2 font-bold uppercase tracking-wider">Neural Focus (Grad-CAM)</h3>
          <div className="flex items-center gap-2">
            <div className="group relative">
              <div className="absolute bottom-full left-0 mb-2 w-fit p-2 glass text-xs hidden group-hover:block z-10">
                Visualizes which regions of the spectrogram the neural network focused on most.
              </div>
            </div>
          </div>
        </div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="relative rounded-xl overflow-hidden border border-white/5"
        >
          <img
            src={`data:image/png;base64,${gradcam}`}
            className="w-full h-auto block"
            alt="Grad-CAM Focus Map"
          />
        </motion.div>
      </div>

      <div className="span-6 glass p-6">
        <div className="flex flex-col justify-between items-center mb-6">
            <h3 className="text-md mb-2 font-bold uppercase tracking-wider">Pixel Attribution (IG)</h3>
          <div className="flex items-center gap-2">
            <div className="group relative">
              <div className="absolute text-xs bottom-full left-0 mb-2 w-fit p-2 glass hidden group-hover:block z-10">
                Integrated Gradients show individual pixel contribution to the final decision.
              </div>
            </div>
          </div>
        </div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="relative rounded-xl overflow-hidden border border-white/5"
        >
          <img
            src={`data:image/png;base64,${ig}`}
            className="w-full h-auto block"
            alt="Integrated Gradients Map"
          />
        </motion.div>
      </div>
    </div>
  );
};

export default VisualXAI;
