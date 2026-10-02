const ScoreCard = ({ title, score, maxScore = 100, icon: Icon, color = 'blue' }) => {
  
  const getScoreColor = () => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-500';
    if (percentage >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getBgColor = () => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'bg-green-100';
    if (percentage >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const percentage = (score / maxScore) * 100;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 flex flex-col items-center justify-center text-center">
      <div className="flex items-center justify-between w-full mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        {Icon && <Icon className={`w-6 h-6 ${getScoreColor()}`} />}
      </div>
      
      <div className="relative w-32 h-32 flex items-center justify-center">
        {/* Simple circular progress using SVG */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="12"
            fill="transparent"
            className="text-gray-100"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="currentColor"
            strokeWidth="12"
            fill="transparent"
            strokeDasharray={2 * Math.PI * 56}
            strokeDashoffset={(2 * Math.PI * 56) * (1 - percentage / 100)}
            className={`${getScoreColor()} transition-all duration-1000 ease-out`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${getScoreColor()}`}>{score}</span>
          <span className="text-xs text-gray-500">/ {maxScore}</span>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard;
