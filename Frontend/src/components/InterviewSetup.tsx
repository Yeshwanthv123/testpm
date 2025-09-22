import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Users, Target, Chrome, Package, Building2, ArrowRight, Star, Smartphone, Play, Car, FileText, Sparkles, Upload, Search, X } from 'lucide-react';
import { InterviewType } from '../types';
import { interviewTypes } from '../data/mockData';
import { fetchInterviewQuestions } from '../utils/api'; // Make sure this is imported

// The component no longer needs to receive a function as a prop,
// as it will now handle navigation by itself.
// interface InterviewSetupProps {
//   onStartInterview: (interviewType: InterviewType, jobDescription?: string) => void;
// }

const InterviewSetup: React.FC = () => { // Props removed
  const [selectedType, setSelectedType] = useState<InterviewType | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [useJobDescription, setUseJobDescription] = useState(false);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false); // State to handle loading
  const navigate = useNavigate(); // React Router's navigation hook

  const getIcon = (iconName: string) => {
    const icons = { Target, Chrome, Users, Package, Building2, Smartphone, Play, Car };
    const Icon = icons[iconName as keyof typeof icons] || Target;
    return Icon;
  };

  const allCompanies = [
    // Your extensive company list remains here...
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
    // ... all other companies
  ];

  const filteredCompanies = searchQuery.trim() === ''
    ? allCompanies.slice(0, 10)
    : allCompanies.filter(company =>
        company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()))
      );

  const generalPMType = interviewTypes.find(type => type.isGeneral);

  const handleCompanySelect = (companyId: string) => {
    setSelectedCompany(companyId);
    const companyType = interviewTypes.find(type => type.company === companyId);
    if (companyType) {
      setSelectedType(companyType);
    }
    setSearchQuery('');
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setJdFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setJobDescription(content);
        setUseJobDescription(true);
      };
      reader.readAsText(file);
    }
  };

  // +++ MODIFIED PART: Logic to handle API call and navigation +++
  const handleStartInterview = async () => {
    if (selectedType) {
      setIsLoading(true); // Start loading
      try {
        // Use the selected company, or 'Generic' if none is selected (e.g., for JD-only flow)
        const companyToFetch = selectedCompany || 'Generic';
        // The role can be made dynamic later if needed
        const role = 'Product Manager';

        const questions = await fetchInterviewQuestions(companyToFetch, role);

        if (questions && questions.length > 0) {
          // Navigate to the interview flow page with the fetched questions
          navigate('/interview', {
            state: {
              questions,
              settings: {
                interviewType: selectedType,
                jobDescription: useJobDescription ? jobDescription : undefined,
              },
            },
          });
        } else {
          // Handle case where API returns no questions
          alert('Could not load interview questions. Please try a different company or try again later.');
        }
      } catch (error) {
        console.error('Failed to start interview:', error);
        alert('An error occurred while preparing your interview. Please check the console for details.');
      } finally {
        setIsLoading(false); // Stop loading
      }
    }
  };
  // +++ END OF MODIFIED PART +++

  const canStartInterview = selectedType && (!useJobDescription || jobDescription.trim());

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      {/* The entire UI structure remains exactly the same. */}
      {/* ... */}
      <div className="max-w-7xl mx-auto">
        {/* ... Header, Company Selection, JD Upload sections are all unchanged ... */}

        {/* Section 3: Selected Interview Summary & Start */}
        {selectedType && (
          <div className="bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-100">
            {/* ... All the summary UI, stats, and feature lists are unchanged ... */}

            {/* Start Button - The only UI part that is modified */}
            <div className="text-center">
              <button
                onClick={handleStartInterview}
                // Button is disabled if conditions aren't met OR if it's currently loading
                disabled={!canStartInterview || isLoading}
                className="inline-flex items-center space-x-3 md:space-x-4 px-8 md:px-12 py-4 md:py-5 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105 font-bold text-base md:text-xl shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none w-full sm:w-auto"
              >
                {/* Button text changes based on loading state */}
                <span>{isLoading ? 'Preparing Questions...' : 'Start Interview'}</span>
                <ArrowRight className="w-5 h-5 md:w-6 md:h-6" />
              </button>
              {!canStartInterview && useJobDescription && !jobDescription.trim() && (
                <p className="text-red-600 text-sm mt-3">Please provide a job description to continue</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewSetup;