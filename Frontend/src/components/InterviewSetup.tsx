import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react'; // Simplified imports for brevity
import { InterviewType } from '../types';
import { interviewTypes } from '../data/mockData';
import { fetchInterviewQuestions } from '../utils/api';

// NOTE: The UI code for this component is extensive. 
// The key change is in the 'handleStartInterview' function and the button's state.
// The rest of your JSX and company list data can remain as it is.

const InterviewSetup: React.FC = () => {
  const [selectedType, setSelectedType] = useState<InterviewType | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [useJobDescription, setUseJobDescription] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // All your existing UI logic (getIcon, allCompanies, filteredCompanies, etc.) goes here...

  const handleCompanySelect = (companyId: string) => {
    setSelectedCompany(companyId);
    const companyType = interviewTypes.find(type => type.company === companyId);
    if (companyType) {
      setSelectedType(companyType);
    }
    setSearchQuery('');
  };

  const handleStartInterview = async () => {
    if (selectedType) {
      setIsLoading(true);
      try {
        const companyToFetch = selectedCompany || 'Generic';
        const role = 'Product Manager'; // Can be made dynamic later
        const questions = await fetchInterviewQuestions(companyToFetch, role);

        if (questions && questions.length > 0) {
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
          alert('Could not load interview questions. The database might be empty or the company not found.');
        }
      } catch (error) {
        console.error('Failed to start interview:', error);
        alert('An error occurred while setting up the interview.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const canStartInterview = !!selectedType && (!useJobDescription || !!jobDescription.trim());
  
  // Render your full JSX here. The important part is the button:
  return (
    <div>
      {/* ... all your other JSX ... */}
      {selectedType && (
        <div /* Summary section */>
          {/* ... */}
          <button
            onClick={handleStartInterview}
            disabled={!canStartInterview || isLoading}
            className="... your classes ..."
          >
            <span>{isLoading ? 'Preparing Questions...' : 'Start Interview'}</span>
            <ArrowRight className="w-5 h-5" />
          </button>
          {/* ... */}
        </div>
      )}
    </div>
  );
};

export default InterviewSetup;