import { useState } from 'react';
import { ChevronDown, ChevronUp, Briefcase } from 'lucide-react';
import SkillBadge from './SkillBadge';

const JobCard = ({ job }) => {
  const [expanded, setExpanded] = useState(false);
  const { title, company, matchScore, skillMatch, explanation, suggestedSkills } = job;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      <div className="p-6 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex justify-between items-start">
          <div className="flex gap-4">
            <div className="mt-1 bg-blue-50 p-3 rounded-lg text-blue-600">
              <Briefcase className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{title}</h3>
              <p className="text-gray-600 font-medium">{company}</p>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-lg border font-bold flex flex-col items-center justify-center ${getScoreColor(matchScore)}`}>
            <span className="text-2xl leading-none">{matchScore}%</span>
            <span className="text-xs uppercase tracking-wider mt-1">Match</span>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
          <span>{skillMatch?.matched?.length || 0} matching skills</span>
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </div>

      {expanded && (
        <div className="px-6 pb-6 pt-2 border-t border-gray-100 bg-gray-50">
          <p className="text-gray-700 mt-4 mb-6 leading-relaxed">
            {explanation}
          </p>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Matched Skills</h4>
              <div className="flex flex-wrap gap-2">
                {skillMatch?.matched?.map((skill, i) => (
                  <SkillBadge key={i} skill={skill} type="matched" />
                ))}
                {(!skillMatch?.matched || skillMatch.matched.length === 0) && (
                  <span className="text-gray-500 text-sm">None</span>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">Skills to Learn</h4>
              <div className="flex flex-wrap gap-2">
                {suggestedSkills?.map((skill, i) => (
                  <SkillBadge key={i} skill={skill} type="missing" />
                ))}
                {(!suggestedSkills || suggestedSkills.length === 0) && (
                  <span className="text-gray-500 text-sm">None</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobCard;
