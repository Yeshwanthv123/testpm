// PDF Download Utility for Interview Results
// Downloads as HTML file that can be printed or converted to PDF

export const downloadInterviewResults = async (results: any, filename: string = 'interview-results.html') => {
  try {
    // Create HTML content
    const htmlContent = generateReportHTML(results);
    
    // Create blob with proper filename
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    
    // Create download link
    const link = document.createElement('a');
    const url = window.URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename.replace('.pdf', '.html'));
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('Failed to generate report:', error);
    // Fallback: download as JSON
    downloadResultsJSON(results, filename.replace('.pdf', '.json'));
    return false;
  }
};

function generateReportHTML(results: any): string {
  const perQuestion = results.perQuestionEvaluations || results.per_question || [];
  const username = results.username || results.user?.full_name || results.user?.email?.split('@')[0] || 'User';
  const region = results.region || results.user?.region || 'Not specified';
  const experience = results.experience || results.user?.experience || 'Not specified';
  const questionCount = perQuestion.length;
  
  const questionsHTML = perQuestion.map((item: any, idx: number) => {
    const questionText = item.question?.question || item.question?.text || '';
    const company = item.question?.company || 'General';
    const score = item.score || 0;
    const strengths = (item.strengths || []).map((s: string) => `<li>${s}</li>`).join('');
    const weaknesses = (item.weaknesses || []).map((w: string) => `<li>${w}</li>`).join('');
    const feedback = item.feedback || '';
    
    return `
      <div style="page-break-inside: avoid; margin: 20px 0; border: 1px solid #ddd; padding: 15px;">
        <h3>Q${idx + 1}: ${company}</h3>
        <p><strong>Question:</strong> ${questionText}</p>
        <p><strong>Score:</strong> <span style="color: #4CAF50; font-weight: bold;">${score}/100</span></p>
        ${strengths ? `<div><strong>Strengths:</strong><ul>${strengths}</ul></div>` : ''}
        ${weaknesses ? `<div><strong>Areas for Improvement:</strong><ul>${weaknesses}</ul></div>` : ''}
        ${feedback ? `<div><strong>Feedback:</strong> ${feedback}</div>` : ''}
      </div>
    `;
  }).join('');
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Interview Performance Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
        h1 { color: #0066cc; text-align: center; }
        h2 { color: #333; margin-top: 30px; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #0066cc; padding-bottom: 20px; }
        .logo { text-align: center; margin-bottom: 15px; font-size: 32px; font-weight: bold; color: #FF9900; }
        .user-info { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .user-info-item { padding: 10px; background: white; border-radius: 3px; }
        .user-info-label { font-weight: bold; color: #0066cc; font-size: 12px; text-transform: uppercase; }
        .user-info-value { font-size: 14px; margin-top: 5px; }
        .score-box { background: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0; }
        .score-box h2 { margin: 0; color: #0066cc; }
        .metadata { text-align: center; margin: 10px 0; font-size: 14px; }
        ul { margin: 10px 0; }
        li { margin: 5px 0; }
        @media print { body { margin: 0; } }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="logo">🧠 PM BOT</div>
        <h1>Interview Performance Report</h1>
        <p style="color: #666; margin: 5px 0;">Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
      </div>
      
      <div class="user-info">
        <div class="user-info-item">
          <div class="user-info-label">👤 Candidate Name</div>
          <div class="user-info-value">${username || 'Not specified'}</div>
        </div>
        <div class="user-info-item">
          <div class="user-info-label">🌍 Region</div>
          <div class="user-info-value">${region || 'Not specified'}</div>
        </div>
        <div class="user-info-item">
          <div class="user-info-label">💼 Experience Level</div>
          <div class="user-info-value">${experience || 'Not specified'}</div>
        </div>
        <div class="user-info-item">
          <div class="user-info-label">📊 Questions Attempted</div>
          <div class="user-info-value">${questionCount}</div>
        </div>
      </div>
      
      <div class="score-box">
        <h2>Overall Score: ${results.overallScore || results.overall_score || 0}/100</h2>
        <div class="metadata">Out of ${questionCount} questions</div>
      </div>
      
      <h2>Question-wise Analysis</h2>
      ${questionsHTML}
      
      <p style="margin-top: 40px; text-align: center; color: #999; font-size: 12px;">
        Generated by PM Bot Interview Platform | www.pmbot.io
      </p>
    </body>
    </html>
  `;
}

// Download as JSON
export const downloadResultsJSON = (results: any, filename: string = 'interview-results.json') => {
  try {
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', filename);
    linkElement.click();
    return true;
  } catch (error) {
    console.error('Failed to download JSON:', error);
    return false;
  }
};

// Download as CSV
export const downloadResultsCSV = (results: any, filename: string = 'interview-results.csv') => {
  try {
    const username = results.username || results.user?.full_name || results.user?.email?.split('@')[0] || 'User';
    const region = results.region || results.user?.region || 'Not specified';
    const experience = results.experience || results.user?.experience || 'Not specified';
    const perQuestion = results.per_question || [];
    
    // Start with metadata
    let csv = 'PM Bot Interview Results\n';
    csv += `Generated on,${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n`;
    csv += `Candidate Name,${username}\n`;
    csv += `Region,${region}\n`;
    csv += `Experience Level,${experience}\n`;
    csv += `Overall Score,"${results.overall_score || 0}/100"\n`;
    csv += `Questions Attempted,${perQuestion.length}\n\n`;
    
    // Add question data header
    csv += 'Question #,Company,Category,Score,Strengths,Weaknesses,Feedback\n';
    
    if (Array.isArray(perQuestion)) {
      perQuestion.forEach((item: any, index: number) => {
        const company = item.question?.company || 'General';
        const category = item.question?.category || 'General';
        const score = item.score || 0;
        const strengths = (item.strengths || []).join('; ').replace(/"/g, '""');
        const weaknesses = (item.weaknesses || []).join('; ').replace(/"/g, '""');
        const feedback = (item.feedback || '').replace(/"/g, '""');
        
        csv += `"Q${index + 1}","${company}","${category}","${score}","${strengths}","${weaknesses}","${feedback}"\n`;
      });
    }
    
    const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', filename);
    linkElement.click();
    return true;
  } catch (error) {
    console.error('Failed to generate CSV:', error);
    return false;
  }
};
