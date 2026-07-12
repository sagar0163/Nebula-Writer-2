// Onboarding Wizard Component for Nebula-Writer
// Guided project creation from 3-sentence pitch to full Codex

const OnboardingWizard = {
  template: `
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div class="w-full max-w-3xl max-h-[90vh] overflow-y-auto glass-premium rounded-3xl animate-in slide-in-from-bottom-4 duration-300">
        <!-- Progress Bar -->
        <div class="p-6 border-b border-space-600">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-xl font-heading font-semibold">Create Your Story</h2>
            <span class="text-sm text-slate-400">{{ currentStep + 1 }} of {{ totalSteps }}</span>
          </div>
          <div class="h-2 bg-space-700 rounded-full overflow-hidden">
            <div 
              class="h-full bg-gradient-to-r from-violet-500 to-indigo-500 transition-all duration-500 ease-out"
              :style="{ width: progressPercent + '%' }"
            ></div>
          </div>
          <div class="flex justify-between text-xs text-slate-500 mt-2">
            <span :class="{ 'text-violet-400 font-medium': currentStep === 0 }">Concept</span>
            <span :class="{ 'text-violet-400 font-medium': currentStep === 1 }">Genre</span>
            <span :class="{ 'text-violet-400 font-medium': currentStep === 2 }">Characters</span>
            <span :class="{ 'text-violet-400 font-medium': currentStep === 3 }">Generate</span>
          </div>
        </div>

        <!-- Step Content -->
        <div class="p-6 space-y-6">
          <!-- Step 1: Concept -->
          <div v-if="currentStep === 0" class="animate-in fade-in duration-300">
            <h3 class="text-lg font-semibold">What's your story about?</h3>
            <p class="text-slate-400 text-sm mb-4">Describe your story in 2-3 sentences. We'll build a complete Codex from this.</p>
            <textarea 
              v-model="form.concept"
              rows="4"
              class="input-field w-full p-4 rounded-xl text-slate-100 placeholder-slate-500 resize-none focus:ring-2 focus:ring-violet-500/20"
              placeholder="Example: A retired detective with memory loss discovers his old cases are being recreated by a serial killer. As he investigates, he realizes the killer knows things only the original investigator would know. The truth forces him to confront what he chose to forget."
              @keydown.enter.prevent
            ></textarea>
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <span class="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 font-mono">{{ form.concept.length }}/500 </span>
              <span v-if="form.concept.length > 20" class="text-emerald-400">✓ Great start!</span>
            </div>
          </div>

          <!-- Step 2: Genre & Templates -->
          <div v-if="currentStep === 1" class="animate-in fade-in duration-300">
            <h3 class="text-lg font-semibold">Choose your genre</h3>
            <p class="text-slate-400 text-sm mb-4">Select a template or start blank. Templates include characters, locations, plot threads, and world rules.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <template v-for="template in templates" :key="template.id">
                <button
                  @click="selectTemplate(template)"
                  :class="[
                    'p-4 rounded-2xl border-2 transition-all relative group',
                    selectedTemplate === template.id 
                      ? 'border-violet-500 bg-violet-500/10' 
                      : 'border-space-600 hover:border-violet-500/50'
                  ]"
                  class="text-left"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
                      <span class="text-2xl">{{ template.icon }}</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <h4 class="font-semibold text-white group-hover:text-violet-300 transition-colors">{{ template.name }}</h4>
                      <p class="text-sm text-slate-400 mt-1 line-clamp-2">{{ template.description }}</p>
                      <div class="flex flex-wrap gap-1 mt-2">
                        <span v-for="tag in template.tags.slice(0,3)" :key="tag" 
                          class="px-2 py-0.5 text-xs bg-space-700 border border-space-600 rounded text-slate-300"
                        >{{ tag }}</span>
                      </div>
                    </div>
                    <div v-if="selectedTemplate === template.id" class="absolute -top-2 -right-2 w-6 h-6 bg-violet-500 rounded-full flex items-center justify-center text-white text-sm font-bold">✓</div>
                  </div>
                </button>
              </template>
            </div>
            
            <button 
              @click="selectTemplate(null)"
              :class="[
                'w-full p-4 rounded-2xl border-2 transition-all',
                !selectedTemplate ? 'border-violet-500 bg-violet-500/10' : 'border-space-600 hover:border-violet-500/50'
              ]"
              class="text-center"
            >
              <svg class="w-6 h-6 mx-auto mb-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              <span class="text-slate-300">Start from scratch</span>
            </button>
          </div>

          <!-- Step 3: Character Customization -->
          <div v-if="currentStep === 2" class="animate-in fade-in duration-300">
            <h3 class="text-lg font-semibold">Your cast of characters</h3>
            <p class="text-slate-400 text-sm mb-4">{{ selectedTemplate ? 'Review and customize the generated characters' : 'Add your main characters' }}</p>
            
            <div v-if="generatedCharacters.length === 0 && !selectedTemplate" class="text-center py-8">
              <svg class="w-12 h-12 mx-auto text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <p class="text-slate-400">No characters yet. Add your first character below.</p>
            </div>
            
            <div v-if="generatedCharacters.length > 0" class="space-y-3 max-h-64 overflow-y-auto">
              <div v-for="(char, idx) in generatedCharacters" :key="idx" 
                class="p-4 rounded-xl border border-space-600 hover:border-violet-500/50 transition-colors">
                <div class="flex items-start gap-3">
                  <input type="checkbox" v-model="char.included" class="mt-1 w-5 h-5 text-violet-500 border-space-600 rounded focus:ring-violet-500" />
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <h4 class="font-semibold text-white">{{ char.name }}</h4>
                      <span class="px-2 py-0.5 text-xs bg-violet-500/20 text-violet-300 rounded">{{ char.role }}</span>
                    </div>
                    <p class="text-sm text-slate-400 mt-1 line-clamp-2">{{ char.description }}</p>
                    <div class="flex flex-wrap gap-1 mt-2">
                      <span v-for="(val, key) in char.attributes" :key="key" class="px-2 py-0.5 text-xs bg-space-700 border border-space-600 rounded text-slate-300">{{ key }}: {{ val }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <button @click="addCustomCharacter" class="w-full mt-4 btn-secondary py-3 rounded-xl font-medium flex items-center justify-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
              <span>Add Custom Character</span>
            </button>
          </div>

          <!-- Step 4: Generate & Launch -->
          <div v-if="currentStep === 3" class="animate-in fade-in duration-300 text-center py-8">
            <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center animate-pulse">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">Ready to generate your Codex?</h3>
            <p class="text-slate-400 mb-6 max-w-md mx-auto">We'll create your complete story bible with characters, locations, plot threads, world rules, and foreshadowing. Then you can start writing Chapter 1.</p>
            
            <div class="space-y-2 text-left max-w-md mx-auto text-sm">
              <div class="flex items-center gap-2 text-slate-300">
                <span class="w-5 h-5 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 text-xs">1</span>
                <span>{{ form.concept.length > 20 ? 'Concept captured' : 'Concept needed' }}</span>
              </div>
              <div class="flex items-center gap-2 text-slate-300">
                <span class="w-5 h-5 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 text-xs">2</span>
                <span>{{ selectedTemplate ? 'Genre: ' + getTemplateName(selectedTemplate) : 'Using custom setup' }}</span>
              </div>
              <div class="flex items-center gap-2 text-slate-300">
                <span class="w-5 h-5 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 text-xs">3</span>
                <span>{{ generatedCharacters.filter(c => c.included).length }} characters ready</span>
              </div>
            </div>
            
            <button 
              @click="generateCodex"
              :disabled="generating || !form.concept || form.concept.length < 20"
              class="btn-primary w-full py-4 rounded-xl font-semibold text-lg mt-8 shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="generating" class="flex items-center justify-center gap-2">
                <svg class="animate-spin w-5 h-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Generating your Codex...
              </span>
              <span v-else>Generate Codex & Start Writing</span>
            </button>
            
            <p v-if="generationError" class="text-red-400 text-sm mt-4">{{ generationError }}</p>
          </div>
        </div>

        <!-- Navigation -->
        <div class="p-6 border-t border-space-600 flex justify-between">
          <button 
            v-if="currentStep > 0"
            @click="prevStep"
            class="btn-secondary px-6 py-2 rounded-xl font-medium"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
            Back
          </button>
          <div v-else class="w-24"></div>
          
          <button 
            v-if="currentStep < totalSteps - 1"
            @click="nextStep"
            :disabled="!canProceed"
            class="btn-primary px-6 py-2 rounded-xl font-medium disabled:opacity-50"
          >
            Next
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
          <button 
            v-else
            @click="closeWizard"
            class="btn-secondary px-6 py-2 rounded-xl font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  `,
  
  props: {
    show: Boolean,
    onComplete: Function,
    onClose: Function
  },
  
  data() {
    return {
      currentStep: 0,
      totalSteps: 4,
      form: {
        concept: ''
      },
      selectedTemplate: null,
      generatedCharacters: [],
      generating: false,
      generationError: null,
      customCharacters: [],
      templates: [
        {
          id: 'epic_fantasy',
          name: 'Epic Fantasy',
          icon: '🏰',
          description: 'High fantasy with magic systems, multiple POVs, and world-spanning stakes',
          description_full: 'Magic systems, multiple POVs, world-spanning stakes, chosen ones, dark lords',
          tags: ['magic', 'multiple-pov', 'world-building', 'chosen-one', 'dark-lord'],
          file: 'epic_fantasy.json'
        },
        {
          id: 'contemporary_romance',
          name: 'Contemporary Romance',
          icon: '💕',
          description: 'Character-driven love story with emotional depth, realistic obstacles, and satisfying HEA',
          description_full: 'HEA guaranteed, emotional depth, dual POV, trope-friendly, series potential',
          tags: ['HEA-guaranteed', 'emotional-depth', 'dual-POV', 'trope-friendly', 'series-potential'],
          file: 'contemporary_romance.json'
        },
        {
          id: 'psychological_thriller',
          name: 'Psychological Thriller',
          icon: '🧠',
          description: 'Unreliable narrator, memory gaps, gaslighting, twists that reframe everything',
          description_full: 'Unreliable narrator, memory loss, gaslighting, plot twists, dark atmosphere',
          tags: ['unreliable-narrator', 'memory-loss', 'gaslighting', 'plot-twist', 'dark'],
          file: 'psychological_thriller.json'
        },
        {
          id: 'hard_scifi',
          name: 'Hard Sci-Fi',
          icon: '🚀',
          description: 'Realistic physics, near-future tech, scientific accuracy over space opera',
          description_full: 'Realistic physics, near-future tech, scientific accuracy, no FTL, hard tech',
          tags: ['realistic-physics', 'near-future', 'scientific-accuracy', 'no-FTL', 'hard-tech'],
          file: 'hard_scifi.json'
        },
        {
          id: 'cozy_mystery',
          name: 'Cozy Mystery',
          icon: '🔍',
          description: 'Light-hearted whodunit in a charming small town with an amateur sleuth',
          description_full: 'Amateur sleuth, small town, no gore, recipe included, recurring cast',
          tags: ['amateur-sleuth', 'small-town', 'no-gore', 'recipe-included', 'recurring-cast'],
          file: 'cozy_mystery.json'
        }
      ]
    };
  },
  
  computed: {
    progressPercent() {
      return ((this.currentStep + 1) / this.totalSteps) * 100;
    },
    
    canProceed() {
      switch(this.currentStep) {
        case 0: return this.form.concept.length >= 20;
        case 1: return true; // Template optional
        case 2: return this.generatedCharacters.some(c => c.included) || this.customCharacters.length > 0;
        default: return true;
      }
    }
  },
  
  watch: {
    show(val) {
      if (val) {
        this.resetWizard();
      }
    }
  },
  
  methods: {
    resetWizard() {
      this.currentStep = 0;
      this.form.concept = '';
      this.selectedTemplate = null;
      this.generatedCharacters = [];
      this.customCharacters = [];
      this.generating = false;
      this.generationError = null;
    },
    
    selectTemplate(template) {
      this.selectedTemplate = template?.id || null;
      if (template) {
        this.loadTemplate(template.file);
      } else {
        this.generatedCharacters = [];
      }
    },
    
    async loadTemplate(file) {
      try {
        const response = await fetch(`/templates/${file}`);
        if (!response.ok) throw new Error('Template not found');
        const data = await response.json();
        this.generatedCharacters = (data.entities || [])
          .filter(e => e.entity_type === 'character')
          .map((e, i) => ({
            id: `char_${i}`,
            name: e.name,
            role: e.attributes?.role || 'character',
            description: e.description,
            attributes: e.attributes || {},
            included: true
          }));
      } catch (e) {
        console.error('Failed to load template:', e);
        this.generatedCharacters = [];
      }
    },
    
    getTemplateName(id) {
      const t = this.templates.find(t => t.id === id);
      return t ? t.name : id;
    },
    
    addCustomCharacter() {
      this.customCharacters.push({
        id: `custom_${Date.now()}`,
        name: '',
        role: 'character',
        description: '',
        attributes: { role: 'custom' },
        included: true,
        isCustom: true
      });
      this.currentStep = 2; // Ensure we're on character step
      // Focus the new character input
      this.$nextTick(() => {
        const inputs = document.querySelectorAll('.custom-char-input');
        if (inputs.length) inputs[inputs.length - 1].focus();
      });
    },
    
    async generateCodex() {
      if (!this.form.concept || this.form.concept.length < 20) return;
      
      this.generating = true;
      this.generationError = null;
      
      try {
        // Build the payload
        const payload = {
          concept: this.form.concept,
          template: this.selectedTemplate,
          characters: [
            ...this.generatedCharacters.filter(c => c.included).map(c => ({
              name: c.name,
              entity_type: 'character',
              description: c.description,
              attributes: Object.entries(c.attributes).map(([k, v]) => ({ key: k, value: v }))
            })),
            ...this.customCharacters.filter(c => c.included && c.name).map(c => ({
              name: c.name,
              entity_type: 'character',
              description: c.description,
              attributes: Object.entries(c.attributes).map(([k, v]) => ({ key: k, value: v }))
            }))
          ]
        };
        
        // Call the architect endpoint to generate full Codex
        const response = await fetch('http://localhost:8000/api/architect/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || 'Generation failed');
        }
        
        const result = await response.json();
        
        // Notify parent component
        this.$emit('complete', result);
        this.closeWizard();
        
      } catch (e) {
        this.generationError = e.message;
        console.error('Codex generation failed:', e);
      } finally {
        this.generating = false;
      }
    },
    
    nextStep() {
      if (this.canProceed && this.currentStep < this.totalSteps - 1) {
        this.currentStep++;
        // Auto-load template characters when moving to character step
        if (this.currentStep === 2 && this.selectedTemplate && this.generatedCharacters.length === 0) {
          this.loadTemplate(this.templates.find(t => t.id === this.selectedTemplate).file);
        }
      }
    },
    
    prevStep() {
      if (this.currentStep > 0) this.currentStep--;
    },
    
    closeWizard() {
      this.$emit('close');
      this.resetWizard();
    }
  }
};

// Register globally
if (typeof window !== 'undefined') {
  window.OnboardingWizard = OnboardingWizard;
}