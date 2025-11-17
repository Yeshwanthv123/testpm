import React, { useState } from 'react';
import { Clock, Users, Target, Chrome, Package, Building2, ArrowRight, Star, Smartphone, Play, Car, FileText, Sparkles, Upload, Search, X, Loader2 } from 'lucide-react';
import { InterviewType, Question, User } from '../types';
import { interviewTypes } from '../data/mockData';
import { fetchInterviewQuestions } from '../utils/api';

interface InterviewSetupProps {
  user: User;
  onStartInterview: (interviewType: InterviewType, questions: Question[], jobDescription?: string) => void;
}

const InterviewSetup: React.FC<InterviewSetupProps> = ({ user, onStartInterview }) => {
  const [selectedType, setSelectedType] = useState<InterviewType | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [useJobDescription, setUseJobDescription] = useState(false);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [isFetchingQuestions, setIsFetchingQuestions] = useState(false);

  const getIcon = (iconName: string) => {
    const icons = {
      Target,
      Chrome,
      Users,
      Package,
      Building2,
      Smartphone,
      Play,
      Car
    };
    const Icon = icons[iconName as keyof typeof icons] || Target;
    return Icon;
  };

  // --- helpers: keep logic stable with backend expectations ---
  
  // Extended company list with search functionality
  const allCompanies = [
    { 
      id: 'Google', 
      name: 'Google', 
      category: 'Tech',
      keywords: ['google', 'alphabet', 'search', 'android', 'chrome'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
        </div>
      ),
      color: 'from-red-500 to-yellow-500' 
    },
    { 
      id: 'Meta', 
      name: 'Meta', 
      category: 'Social Media',
      keywords: ['meta', 'facebook', 'instagram', 'whatsapp', 'social'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
        </div>
      ),
      color: 'from-blue-600 to-purple-600' 
    },
    { 
      id: 'Amazon', 
      name: 'Amazon', 
      category: 'E-commerce',
      keywords: ['amazon', 'aws', 'ecommerce', 'cloud', 'retail'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#FF9900" d="M.045 18.02c.072-.116.187-.124.348-.022 3.636 2.11 7.594 3.166 11.87 3.166 2.852 0 5.668-.533 8.447-1.595l.315-.14c.138-.06.234-.1.293-.13.226-.088.39-.046.525.13.12.174.09.336-.12.48-.256.19-.6.41-1.006.654-1.244.743-2.64 1.316-4.185 1.726-1.53.406-3.045.61-4.516.61-2.265 0-4.463-.356-6.604-1.07-2.09-.698-3.99-1.726-5.715-3.08-.267-.21-.31-.404-.13-.63l-.522-.1z"/>
            <path fill="#FF9900" d="M20.409 15.023c-.196-.497-.73-.818-1.604-1.01-1.17-.256-2.174-.135-3.01.365-.835.5-1.253 1.132-1.253 1.895 0 .763.418 1.395 1.253 1.895.836.5 1.84.621 3.01.365.874-.192 1.408-.513 1.604-1.01.196-.497.196-.997 0-1.5z"/>
            <path fill="#232F3E" d="M8.095 8.095c.4-.4.4-1.05 0-1.45-.4-.4-1.05-.4-1.45 0l-3.2 3.2c-.4.4-.4 1.05 0 1.45l3.2 3.2c.4.4 1.05.4 1.45 0 .4-.4.4-1.05 0-1.45L5.545 10.5h8.955c.55 0 1-.45 1-1s-.45-1-1-1H5.545l2.55-2.55z"/>
          </svg>
        </div>
      ),
      color: 'from-orange-500 to-yellow-500' 
    },
    { 
      id: 'Microsoft', 
      name: 'Microsoft', 
      category: 'Tech',
      keywords: ['microsoft', 'windows', 'office', 'azure', 'teams'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#F25022" d="M1 1h10v10H1z"/>
            <path fill="#00A4EF" d="M13 1h10v10H13z"/>
            <path fill="#7FBA00" d="M1 13h10v10H1z"/>
            <path fill="#FFB900" d="M13 13h10v10H13z"/>
          </svg>
        </div>
      ),
      color: 'from-blue-500 to-teal-500' 
    },
    { 
      id: 'Apple', 
      name: 'Apple', 
      category: 'Tech',
      keywords: ['apple', 'iphone', 'mac', 'ios', 'design'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#000000" d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
          </svg>
        </div>
      ),
      color: 'from-gray-600 to-gray-800' 
    },
    { 
      id: 'Netflix', 
      name: 'Netflix', 
      category: 'Entertainment',
      keywords: ['netflix', 'streaming', 'entertainment', 'content', 'video'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#E50914" d="M5.398 0v.006c3.028 8.556 5.37 15.175 8.348 23.596 2.344.058 4.85.398 4.854.398-2.8-7.924-5.923-16.747-8.487-24zm8.489 0v9.63L18.6 22.951c-.043-7.86-.004-15.71.002-22.95zM5.398 1.05V24c2.836-.693 4.849-1.133 4.854-1.133V1.05z"/>
          </svg>
        </div>
      ),
      color: 'from-red-600 to-red-800' 
    },
    { 
      id: 'Uber', 
      name: 'Uber', 
      category: 'Transportation',
      keywords: ['uber', 'rideshare', 'transportation', 'mobility', 'delivery'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#000000" d="M16.812 9.6V8.4c0-.663-.537-1.2-1.2-1.2s-1.2.537-1.2 1.2v1.2c0 .663.537 1.2 1.2 1.2s1.2-.537 1.2-1.2zM12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm6 14.4c0 1.325-1.075 2.4-2.4 2.4H8.4c-1.325 0-2.4-1.075-2.4-2.4V9.6c0-1.325 1.075-2.4 2.4-2.4h7.2c1.325 0 2.4 1.075 2.4 2.4v4.8z"/>
          </svg>
        </div>
      ),
      color: 'from-black to-gray-700' 
    },
    { 
      id: 'Salesforce', 
      name: 'Salesforce', 
      category: 'CRM',
      keywords: ['salesforce', 'crm', 'sales', 'cloud', 'customer'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#00A1E0" d="M12.5 2.5c1.7 0 3.2.9 4.1 2.3 1.1-.6 2.4-.8 3.7-.5 2.8.7 4.7 3.2 4.7 6.1 0 .4 0 .8-.1 1.2 1.5 1.1 2.4 2.8 2.4 4.7 0 3.3-2.7 6-6 6H8.5c-3.6 0-6.5-2.9-6.5-6.5 0-2.4 1.3-4.5 3.3-5.6-.1-.5-.1-1-.1-1.5C5.2 5.4 8.1 2.5 12.5 2.5z"/>
          </svg>
        </div>
      ),
      color: 'from-blue-400 to-cyan-500' 
    },
    { 
      id: 'Freshworks', 
      name: 'Freshworks', 
      category: 'SaaS',
      keywords: ['freshworks', 'fresh', 'saas', 'customer', 'support'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#00C896" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
      ),
      color: 'from-green-500 to-emerald-600' 
    },
    { 
      id: 'Zoho', 
      name: 'Zoho', 
      category: 'SaaS',
      keywords: ['zoho', 'crm', 'business', 'software', 'productivity'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#C8202D" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 13h-4l4-6h-4V7h6v2l-4 6h4v2z"/>
          </svg>
        </div>
      ),
      color: 'from-purple-500 to-indigo-600' 
    },
    { 
      id: 'Stripe', 
      name: 'Stripe', 
      category: 'Fintech',
      keywords: ['stripe', 'payments', 'fintech', 'financial', 'api'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#635BFF" d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 2.227 0 4.515.858 6.09 1.631l.89-5.494C18.252.975 15.697 0 12.165 0 9.667 0 7.589.654 6.104 1.872 4.56 3.147 3.757 4.992 3.757 7.218c0 4.039 2.467 5.76 6.476 7.219 2.585.92 3.445 1.574 3.445 2.583 0 .98-.84 1.545-2.354 1.545-1.875 0-4.965-.921-6.99-2.109l-.9 5.555C5.175 22.99 8.385 24 11.714 24c2.641 0 4.843-.624 6.328-1.813 1.664-1.305 2.525-3.236 2.525-5.732 0-4.128-2.524-5.851-6.591-7.305z"/>
          </svg>
        </div>
      ),
      color: 'from-purple-600 to-blue-600' 
    },
    { 
      id: 'Airbnb', 
      name: 'Airbnb', 
      category: 'Travel',
      keywords: ['airbnb', 'travel', 'hospitality', 'booking', 'accommodation'],
      logo: (
        <div className="flex items-center justify-center w-full h-full">
          <svg viewBox="0 0 24 24" className="w-6 h-6">
            <path fill="#FF5A5F" d="M12 0C5.8 0 1.4 5.7 1.4 12.8c0 2.1.5 4.1 1.5 5.8.1.2.3.3.5.3s.4-.1.5-.3c1-1.7 1.5-3.7 1.5-5.8 0-4.4 2.8-8.1 6.6-9.4.2-.1.4-.3.4-.5s-.2-.4-.4-.5C10.2.1 8.1 0 6 0c-.3 0-.5.2-.5.5s.2.5.5.5c1.4 0 2.8.2 4.1.6C5.2 2.9 1.9 7.5 1.9 12.8c0 1.8.4 3.5 1.1 5.1C4.6 20.3 8.1 22 12 22s7.4-1.7 9-4.1c.7-1.6 1.1-3.3 1.1-5.1 0-5.3-3.3-9.9-8.2-11.2 1.3-.4 2.7-.6 4.1-.6.3 0 .5-.2.5-.5s-.2-.5-.5-.5c-2.1 0-4.2.1-6.1.4-.2.1-.4.3-.4.5s.2.4.4.5c3.8 1.3 6.6 5 6.6 9.4 0 2.1.5 4.1 1.5 5.8.1.2.3.3.5.3s.4-.1.5-.3c1-1.7 1.5-3.7 1.5-5.8C22.6 5.7 18.2 0 12 0z"/>
          </svg>
        </div>
      ),
      color: 'from-pink-500 to-red-500' 
    }
  ];

  // Filter companies based on search query
  const filteredCompanies = searchQuery.trim() === '' 
    ? allCompanies.slice(0, 10) // Show first 10 companies when no search
    : allCompanies.filter(company => 
        company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()))
      );

  const generalPMType = interviewTypes.find(type => type.isGeneral);
  // Extract company and role from a pasted Job Description (JD).
  // Goal: return only the company name and a normalized role token like 'PM' or 'Senior PM'.
  function extractCompanyAndRole(jdText: string): { company?: string; role?: string; experience?: string } {
    if (!jdText || jdText.length < 10) return {};
    const s = jdText;

    // 1) Company: look for explicit 'Company:' line
    const companyMatch = s.match(/Company\s*[:\-]\s*([^\n\r]+)/i);
    let company = companyMatch ? companyMatch[1].trim() : undefined;

    // 2) If not found, try to match known companies from the list
    if (!company) {
      const lowered = s.toLowerCase();
      for (const c of allCompanies) {
        if (lowered.includes(c.name.toLowerCase())) {
          company = c.name;
          break;
        }
      }
    }

    // 3) If still not found, try to extract company from first line or "at [CompanyName]" pattern
    if (!company) {
      const atMatch = s.match(/\bat\s+([A-Z][A-Za-z\s&]+?)\s*[,.\n]/);
      if (atMatch) {
        company = atMatch[1].trim();
      }
    }

    // 4) If still not found, try extracting from common job posting patterns
    if (!company) {
      const patterns = [
        /(?:position|role|job)\s+at\s+([A-Z][A-Za-z\s&]+?)(?:\s*-|\s*\n|$)/i,
        /([A-Z][A-Za-z\s&]+?)\s+(?:is hiring|is looking for|seeks|wants)\s+/i,
      ];
      for (const pattern of patterns) {
        const match = s.match(pattern);
        if (match) {
          company = match[1].trim();
          break;
        }
      }
    }

    // 5) Extract experience level from JD
    let experience: string | undefined;
    const lowered = s.toLowerCase();
    if (lowered.includes('10+') || lowered.includes('10 years')) {
      experience = '10+';
    } else if (lowered.includes('senior') || /[5-9]\s*-\s*10|6\s*to\s*10/.test(lowered)) {
      experience = '6-10';
    } else if (/[3-5]\s*-\s*[5-8]|3\s*to\s*5|mid.?level|mid-level/.test(lowered)) {
      experience = '3-5';
    } else if (/[0-2]\s*-\s*3|0\s*to\s*2|entry.?level|junior|associate|apm/i.test(lowered)) {
      experience = '0-2';
    }

    // 6) Role: look for 'Job Title' or 'Title' lines
    const titleMatch = s.match(/Job Title\s*[:\-]\s*([^\n]+)/i) || s.match(/Title\s*[:\-]\s*([^\n]+)/i);
    let rawRole = titleMatch ? titleMatch[1].trim() : undefined;

    // 7) If not found, attempt to find common role phrases
    if (!rawRole) {
      const roleCandidates = [
        /senior\s+product\s+manager/i,
        /product\s+manager/i,
        /associate\s+product\s+manager/i,
        /principal\s+product\s+manager/i,
        /group\s+product\s+manager/i,
        /director/i,
        /head\s+of\s+product/i,
        /pm\b/i
      ];
      for (const rx of roleCandidates) {
        const m = s.match(rx);
        if (m) {
          rawRole = m[0];
          break;
        }
      }
    }

    const roleText = rawRole ? rawRole.toLowerCase() : undefined;
    let role: string | undefined = undefined;
    if (roleText) {
      if (roleText.includes('associate')) role = 'APM';
      else if (roleText.includes('senior') || roleText.includes('sr')) role = 'Senior PM';
      else if (roleText.includes('principal')) role = 'Principal PM';
      else if (roleText.includes('group')) role = 'Group PM';
      else if (roleText.includes('director')) role = 'Director';
      else if (roleText.includes('product') || roleText.includes('pm')) role = 'PM';
    }

    return { company, role, experience };
  }

  // Helper function to get flag emoji for region
  const getRegionFlag = (region: string): string => {
    const flagMap: Record<string, string> = {
      'US': '🇺🇸',
      'EU': '🇬🇧',
      'Asia Pacific': '🇮🇳',
      'BR': '🇧🇷',
      'Africa': '🇿🇦',
      'AE': '🇸🇦',
      'North America': '🇺🇸',
      'Europe': '🇬🇧',
      'South America': '🇧🇷',
      'Middle East': '🇸🇦'
    };
    return flagMap[region] || '🌍';
  };

  // Helper to proceed with JD: selects a sensible default interview type and
  // ensures the summary/start section is visible. This makes the "Proceed with JD"
  // button more reliable across environments.
  const handleProceedWithJD = async () => {
    if (!jobDescription.trim()) return;

    // Validate experience level is set
    if (!user.experience) {
      alert('Please complete your onboarding to set your experience level before proceeding with a job description.');
      return;
    }

    setIsFetchingQuestions(true);

    // Choose a type synchronously so we can pass it to onStartInterview
    const chosenType = generalPMType ?? interviewTypes[0] ?? null;
    if (chosenType) setSelectedType(chosenType);
    setUseJobDescription(true);

    try {
      // Extract company and experience from the pasted JD
      const { company: extractedCompany, experience: extractedExp } = extractCompanyAndRole(jobDescription);
      
      // Use extracted experience level if available, otherwise use user's experience
      const experienceToUse = extractedExp || user.experience;
      const derivedCompany = extractedCompany || selectedCompany || 'Generic';

      const apiResult = await fetchInterviewQuestions({
        company: derivedCompany,
        experience: experienceToUse,
      });

  let questions = (apiResult as unknown) as Question[];

      // If we have no chosenType (edge case), pick a fallback
      const startType = {
        ...(chosenType ?? interviewTypes[0]),
        company: derivedCompany, // Set the extracted/selected company
        name: derivedCompany === 'Generic' ? `PM Interview - ${experienceToUse} exp` : derivedCompany
      };
      onStartInterview(startType as any, questions, jobDescription);

      // Scroll to summary for UX (if rendered)
      setTimeout(() => {
        try {
          const el = document.getElementById('interview-summary');
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch {}
      }, 120);
    } catch (err) {
      console.error('Failed to start interview with JD:', err);
      alert('Failed to start interview from JD. Please try again.');
    } finally {
      setIsFetchingQuestions(false);
    }
  };
  
  const handleCompanySelect = (companyId: string) => {
    setSelectedCompany(companyId);
    const companyType = interviewTypes.find(type => type.company === companyId) || interviewTypes.find(t => t.isGeneral);
    if(companyType) {
        setSelectedType(companyType);
    }
    setSearchQuery(''); // Clear search after selection
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setJdFile(file);

    // Async parse file contents for supported types (pdf, docx, txt, doc fallback)
    (async () => {
      const name = file.name || '';
      const ext = name.split('.').pop()?.toLowerCase() || '';
      try {
        if (ext === 'pdf') {
          // PDF parsing using pdfjs-dist
          // dynamic import so devs without dependency won't break until feature used
          // Use @vite-ignore to avoid static resolution when the package is not installed
          const pkgName = 'pdfjs-dist/legacy/build/pdf';
          // @ts-ignore
          const pdfjs = await import(/* @vite-ignore */ pkgName);
          // try to set workerSrc to CDN; if blocked it's still OK
          try {
            // @ts-ignore
            pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
          } catch {}
          const arrayBuffer = await file.arrayBuffer();
          const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;
          let text = '';
          for (let i = 1; i <= pdf.numPages; i++) {
            // eslint-disable-next-line no-await-in-loop
            const page = await pdf.getPage(i);
            // eslint-disable-next-line no-await-in-loop
            const content = await page.getTextContent();
            const pageText = content.items.map((it: any) => (it.str || '')).join(' ');
            text += pageText + '\n';
          }
          setJobDescription(text);
          setUseJobDescription(true);
          return;
        }

        if (ext === 'docx') {
          // DOCX parsing using mammoth (now a main dependency)
          try {
            // @ts-ignore - mammoth is now installed as a regular dependency
            const mammoth = await import('mammoth');
            const arrayBuffer = await file.arrayBuffer();
            const result = await mammoth.extractRawText({ arrayBuffer });
            const text = (result.value || '').trim();
            if (text && text.length > 10) {
              setJobDescription(text);
              setUseJobDescription(true);
              return;
            }
          } catch (err) {
            console.warn('Mammoth DOCX parsing failed:', err);
            // Fall through to text reading
          }
        }

        // Fallback: read as text for .txt and others
        const txt = await file.text();
        setJobDescription(txt);
        setUseJobDescription(true);
      } catch (err) {
        console.error('Failed to parse uploaded file, falling back to text read', err);
        try {
          const txt = await file.text();
          setJobDescription(txt);
          setUseJobDescription(true);
        } catch (err2) {
          console.error('Failed to read file as text', err2);
        }
      }
    })();
  };

  const handleStartInterview = async () => {
    if (!selectedType || !user.experience) {
      alert("Please select an interview type and ensure your profile is complete (experience level required).");
      return;
    }

    setIsFetchingQuestions(true);
    try {
      let questions: Question[] = [];

      if (useJobDescription && jobDescription.trim()) {
        // JD-aware logic: extract company but use user's experience level for filtering
        const { company: extractedCompany } = extractCompanyAndRole(jobDescription);
        const derivedCompany = extractedCompany || selectedCompany || "Generic";

        const apiResult = await fetchInterviewQuestions({
          company: derivedCompany,
          experience: user.experience,
        });

        questions = (apiResult as unknown) as Question[];
      } else {
        // Original fallback path: use selected company and user's experience level
        const apiResult = await fetchInterviewQuestions({
          company: (selectedCompany || 'Generic'),
          experience: user.experience,
        });
        questions = (apiResult as unknown) as Question[];
      }

      // Extract company name from first question and update interview type name
      const companyFromQuestions = questions?.[0]?.company || selectedCompany || 'General Product Management';
      const updatedInterviewType = {
        ...selectedType,
        name: companyFromQuestions,
      };

      onStartInterview(updatedInterviewType, questions, useJobDescription ? jobDescription : undefined);
    } catch (error) {
      console.error('Failed to start interview:', error);
      alert('Failed to fetch questions. Please try again.');
    } finally {
      setIsFetchingQuestions(false);
    }
  };

  const canStartInterview = selectedType && (!useJobDescription || jobDescription.trim()) && !isFetchingQuestions && (jobDescription.split(/\s+/).length <= 200 || !useJobDescription);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="text-center mb-8 md:mb-16">
          <div className="mb-6 md:mb-8 flex justify-center">
            <div className="w-16 h-16 md:w-20 md:h-20 lg:w-24 lg:h-24 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300">
              <div className="text-3xl md:text-4xl lg:text-5xl">🧠</div>
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6">
            <span className="bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
              Tailor Your Interview Practice, Your Way
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed px-4">
            Get ready for your dream role. Choose a company to simulate a real-world interview, 
            or upload a Job Description (JD) to generate custom questions that match your goals.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 mb-8 md:mb-12">
          {/* Section 1: Company Selection */}
          <div className="bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-100">
            <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-3 mb-6 md:mb-8">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900">Select a Company to Target</h2>
                <p className="text-gray-600 text-sm md:text-base">Pick from our list of top companies or search for the one you're aiming for. We'll tailor your interview experience to that company's style.</p>
              </div>
            </div>

            {/* Smart Search Bar */}
            <div className="mb-6 md:mb-8">
              <div className="flex items-center space-x-2 mb-3">
                <Search className="w-4 h-4 md:w-5 md:h-5 text-gray-500" />
                <span className="font-medium text-gray-700 text-sm md:text-base">Search for a company:</span>
              </div>
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g., Google, Sales, Fintech, Entertainment..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 placeholder-gray-500 pr-10 text-sm md:text-base"
                />
                {searchQuery && (
                  <button
                    onClick={clearSearch}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
                {!searchQuery && (
                  <Search className="absolute right-3 top-3 w-5 h-5 text-gray-400" />
                )}
              </div>
              
              {/* Search Results Info */}
              {searchQuery && (
                <div className="mt-2 text-xs md:text-sm text-gray-600">
                  {filteredCompanies.length > 0 
                    ? `Found ${filteredCompanies.length} companies matching "${searchQuery}"`
                    : `No companies found matching "${searchQuery}"`
                  }
                </div>
              )}
            </div>

            {/* Company Grid */}
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Star className="w-4 h-4 md:w-5 md:h-5 text-yellow-500" />
                <span className="font-medium text-gray-700 text-sm md:text-base">
                  {searchQuery ? 'Search Results:' : 'Popular Companies:'}
                </span>
              </div>
              
              {filteredCompanies.length > 0 ? (
                <div className="grid grid-cols-1 gap-3 max-h-80 md:max-h-96 overflow-y-auto">
                  {filteredCompanies.map((company) => (
                    <button
                      key={company.id}
                      onClick={() => handleCompanySelect(company.id)}
                      className={`p-3 md:p-4 rounded-xl border-2 transition-all transform hover:scale-105 ${
                        selectedCompany === company.id
                          ? 'border-orange-500 bg-gradient-to-r from-orange-50 to-yellow-50 shadow-lg'
                          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 md:w-10 md:h-10 bg-gradient-to-r ${company.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                          {company.logo}
                        </div>
                        <div className="flex-1 text-left min-w-0">
                          <span className="font-medium text-gray-900 text-sm md:text-base block truncate">{company.name}</span>
                          <div className="text-xs text-gray-500">{company.category}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : searchQuery ? (
                <div className="text-center py-6 md:py-8 text-gray-500">
                  <Search className="w-8 h-8 md:w-12 md:h-12 mx-auto mb-3 text-gray-300" />
                  <p className="text-sm md:text-base">No companies found matching your search.</p>
                  <p className="text-xs md:text-sm">Try searching for company names, categories, or keywords.</p>
                </div>
              ) : null}
            </div>
          </div>

          {/* Section 2: Job Description Upload */}
          <div className="bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-100">
            <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-3 mb-6 md:mb-8">
              <div className="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-gray-900">Upload or Paste JD</h2>
                <p className="text-gray-600 text-sm md:text-base">Have a Job Description? Let's customize your prep</p>
              </div>
            </div>

            <p className="text-gray-600 mb-4 md:mb-6 text-sm md:text-base">
              Paste the full JD here or upload a file — our bot will generate interview questions designed for this role.
            </p>

            {/* Toggle for JD Usage */}
            <div className="mb-4 md:mb-6">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useJobDescription}
                  onChange={(e) => setUseJobDescription(e.target.checked)}
                  className="w-4 h-4 md:w-5 md:h-5 text-purple-500 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="font-medium text-gray-700 text-sm md:text-base">Generate custom questions from job description</span>
              </label>
            </div>

            {/* File Upload Area */}
            <div className="mb-4 md:mb-6">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 md:p-6 text-center hover:border-purple-400 transition-colors">
                <input
                  type="file"
                  id="jd-upload"
                  accept=".txt,.doc,.docx,.pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label htmlFor="jd-upload" className="cursor-pointer">
                  <Upload className="w-8 h-8 md:w-12 md:h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2 text-sm md:text-base">Click to upload or drag & drop</p>
                  <p className="text-xs md:text-sm text-gray-500">Supports TXT, DOC, DOCX, PDF files</p>
                </label>
              </div>
              {jdFile && (
                <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-sm text-green-700">✅ File uploaded: {jdFile.name}</p>
                </div>
              )}
            </div>

            {/* Text Area */}
            <div className="mb-4 md:mb-6">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium text-gray-700">Job Description</label>
                {(() => {
                  const wordCount = jobDescription.split(/\s+/).filter(w => w.length > 0).length;
                  const isExceeded = wordCount > 200;
                  return (
                    <span className={`text-xs ${isExceeded ? 'text-red-600 font-semibold' : 'text-gray-500'}`}>
                      {wordCount} / 200 words
                    </span>
                  );
                })()}
              </div>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value.slice(0, 2000))}
                placeholder="Paste your JD here, or drag & drop a file…"
                className={(() => {
                  const wordCount = jobDescription.split(/\s+/).filter(w => w.length > 0).length;
                  const isExceeded = wordCount > 200;
                  const baseClass = 'w-full h-32 md:h-48 p-4 border rounded-xl focus:ring-2 focus:border-transparent resize-none text-gray-900 placeholder-gray-500 text-sm md:text-base';
                  const stateClass = isExceeded ? 'border-red-300 focus:ring-red-500' : 'border-gray-300 focus:ring-purple-500';
                  return `${baseClass} ${stateClass}`;
                })()}
              />
              {(() => {
                const wordCount = jobDescription.split(/\s+/).filter(w => w.length > 0).length;
                return wordCount > 200 ? (
                  <p className="text-xs text-red-600 mt-2">⚠️ Job description should be 200 words or less for optimal AI processing (current: {wordCount} words)</p>
                ) : null;
              })()}
            </div>

            {/* AI Enhancement Info */}
            {useJobDescription && jobDescription && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 md:p-6 border border-purple-200 mb-4 md:mb-6">
                <div className="flex items-start space-x-3">
                  <Sparkles className="w-5 h-5 md:w-6 md:h-6 text-purple-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-purple-900 mb-2 text-sm md:text-base">AI-Powered Question Generation</h4>
                    <p className="text-xs md:text-sm text-purple-800 mb-3">
                      Our AI will analyze the job requirements and create personalized interview questions.
                    </p>
                    <ul className="text-xs text-purple-700 space-y-1">
                      <li>• Extracts key skills and requirements</li>
                      <li>• Generates role-specific scenarios</li>
                      <li>• Adapts difficulty to seniority level</li>
                      <li>• Includes company culture questions</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
              <button
                onClick={() => {
                  setJobDescription('');
                  setJdFile(null);
                  setUseJobDescription(false);
                }}
                className="flex-1 px-4 py-3 border-2 border-purple-300 text-purple-700 rounded-xl hover:bg-purple-50 transition-all font-medium text-sm md:text-base"
              >
                Clear JD
              </button>
              <button
                disabled={!jobDescription.trim()}
                onClick={handleProceedWithJD}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium text-sm md:text-base"
              >
                Proceed with JD
              </button>
            </div>
          </div>
        </div>

        {/* Section 3: Selected Interview Summary & Start */}
        {selectedType && (
          <div id="interview-summary" className="bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-100">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6 md:mb-8">
              <div className="flex-1 mb-6 lg:mb-0">
                <div>
                  <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
                    Ready to start your Product Management interview?
                  </h2>
                  {useJobDescription && jobDescription && (
                    <div className="mb-4 space-y-2">
                      {extractCompanyAndRole(jobDescription).company && (
                        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <p className="text-sm font-semibold text-blue-900">
                            🏢 Company: <span className="text-lg text-blue-600">{extractCompanyAndRole(jobDescription).company}</span>
                          </p>
                        </div>
                      )}
                      {extractCompanyAndRole(jobDescription).experience && (
                        <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                          <p className="text-sm font-semibold text-purple-900">
                            📊 Experience Level: <span className="text-lg text-purple-600">{extractCompanyAndRole(jobDescription).experience} years</span>
                          </p>
                        </div>
                      )}
                      {!extractCompanyAndRole(jobDescription).company && !extractCompanyAndRole(jobDescription).experience && (
                        <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
                          <p className="text-sm text-amber-800">⚠️ Could not extract company or experience level from JD. Using your profile settings.</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <p className="text-base md:text-lg text-gray-600 mb-4">
                  This interview will take approximately {selectedType.duration} minutes and cover {selectedType.questionCount} questions.
                </p>
                {useJobDescription && jobDescription && (
                  <div className="flex items-center space-x-2 mb-4">
                    <Sparkles className="w-4 h-4 md:w-5 md:h-5 text-purple-600" />
                    <span className="text-purple-700 font-medium text-sm md:text-base">
                      Enhanced with AI-generated questions from your job description
                    </span>
                  </div>
                )}
              </div>
              <div className="flex-shrink-0 lg:ml-8 flex justify-center lg:justify-end">
                <div className={`w-16 h-16 md:w-20 md:h-20 rounded-2xl bg-gradient-to-r ${selectedType.color} flex items-center justify-center shadow-lg`}>
                  {selectedType.companyLogo ? (
                    <span className="text-2xl md:text-3xl">{selectedType.companyLogo}</span>
                  ) : (
                    React.createElement(getIcon(selectedType.icon), { className: "w-8 h-8 md:w-10 md:h-10 text-white" })
                  )}
                </div>
              </div>
            </div>

            {/* Interview Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
              <div className="text-center p-4 md:p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl">
                <Clock className="w-6 h-6 md:w-8 md:h-8 text-blue-600 mx-auto mb-3" />
                <div className="font-bold text-lg md:text-xl text-blue-900">{selectedType.duration}</div>
                <div className="text-xs md:text-sm text-blue-700">Minutes</div>
              </div>
              <div className="text-center p-4 md:p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl">
                <Target className="w-6 h-6 md:w-8 md:h-8 text-green-600 mx-auto mb-3" />
                <div className="font-bold text-lg md:text-xl text-green-900">{selectedType.questionCount}</div>
                <div className="text-xs md:text-sm text-green-700">Questions</div>
              </div>
              <div className="text-center p-4 md:p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl">
                <Star className="w-6 h-6 md:w-8 md:h-8 text-yellow-600 mx-auto mb-3" />
                <div className="font-bold text-lg md:text-xl text-yellow-900">AI</div>
                <div className="text-xs md:text-sm text-yellow-700">Evaluation</div>
              </div>
              <div className="text-center p-4 md:p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl">
                <Users className="w-6 h-6 md:w-8 md:h-8 text-purple-600 mx-auto mb-3" />
                <div className="font-bold text-lg md:text-xl text-purple-900">Peer</div>
                <div className="text-xs md:text-sm text-purple-700">Comparison</div>
              </div>
            </div>

            {/* Start Button */}
            <div className="text-center">
              <button
                onClick={handleStartInterview}
                disabled={!canStartInterview}
                className="inline-flex items-center space-x-3 md:space-x-4 px-8 md:px-12 py-4 md:py-5 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-base md:text-xl shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none w-full sm:w-auto"
              >
                {isFetchingQuestions ? (
                    <>
                        <Loader2 className="w-5 h-5 md:w-6 md:h-6 animate-spin" />
                        <span>Preparing Interview...</span>
                    </>
                ) : (
                    <>
                        <span>Start Interview</span>
                        <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
                    </>
                )}
              </button>
              {!canStartInterview && useJobDescription && !jobDescription.trim() && (
                <p className="text-red-600 text-sm mt-3">Please provide a job description to continue</p>
              )}
              {!canStartInterview && useJobDescription && jobDescription.split(/\s+/).length > 200 && (
                <p className="text-red-600 text-sm mt-3">Job description exceeds 200 words. Please reduce by {jobDescription.split(/\s+/).filter(w => w.length > 0).length - 200} words.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewSetup;
