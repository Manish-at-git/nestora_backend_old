with open("../frontend/src/components/DashboardOverview.jsx", "r") as f:
    content = f.read()

new_logic = """
      const isExpired = item.end_date && new Date(item.end_date) < new Date();
      
      let canChangeVote = !isExpired;
      if (item.end_date) {
        const twoHoursBeforeEnd = new Date(new Date(item.end_date).getTime() - 2 * 60 * 60 * 1000);
        if (new Date() >= twoHoursBeforeEnd) {
          canChangeVote = false;
        }
      }
      
      const hasVoted = item.my_votes && item.my_votes.length > 0;
      const showResults = isExpired || hasVoted;

      return (
"""

content = content.replace(
"""
      const isExpired = item.end_date && new Date(item.end_date) < new Date();
      const hasVoted = item.my_votes && item.my_votes.length > 0;
      const showResults = isExpired || hasVoted;

      return (
""", new_logic.strip() + "\n      return ("
)

old_option_render = """
                if (showResults) {
                  return (
                    <div key={opt.id} className="relative bg-slate-50 border border-slate-200 rounded-xl overflow-hidden p-3 z-0">
                      <div 
                        className="absolute inset-y-0 left-0 bg-indigo-100 -z-10 transition-all duration-1000 ease-out"
                        style={{ width: `${opt.vote_percentage || 0}%` }}
                      ></div>
                      <div className="flex justify-between items-center text-sm">
                        <span className={`font-medium ${isSelected ? 'text-indigo-700' : 'text-slate-700'}`}>
                          {opt.option_text || opt.text} {isSelected && '(Your vote)'}
                        </span>
                        <span className="font-bold text-slate-700">{opt.vote_percentage || 0}%</span>
                      </div>
                    </div>
                  );
                }
"""

new_option_render = """
                if (showResults) {
                  return (
                    <button 
                      key={opt.id} 
                      onClick={() => {
                        if (canChangeVote) {
                          handlePollVote(item.id, opt.id, item.is_multiple_choice, item.my_votes || [])
                        }
                      }}
                      disabled={!canChangeVote}
                      className={`relative w-full text-left bg-slate-50 border border-slate-200 rounded-xl overflow-hidden p-3 z-0 ${canChangeVote ? 'cursor-pointer hover:border-indigo-300 transition-colors' : 'cursor-default'}`}
                    >
                      <div 
                        className={`absolute inset-y-0 left-0 -z-10 transition-all duration-1000 ease-out ${isSelected ? 'bg-indigo-200' : 'bg-indigo-100'}`}
                        style={{ width: `${opt.vote_percentage || 0}%` }}
                      ></div>
                      <div className="flex justify-between items-center text-sm">
                        <div className="flex items-center gap-2">
                          {isSelected && <Check size={14} className="text-indigo-700" />}
                          <span className={`font-medium ${isSelected ? 'text-indigo-700' : 'text-slate-700'}`}>
                            {opt.option_text || opt.text}
                          </span>
                        </div>
                        <span className="font-bold text-slate-700">{opt.vote_percentage || 0}%</span>
                      </div>
                    </button>
                  );
                }
"""
content = content.replace(old_option_render.strip(), new_option_render.strip())

with open("../frontend/src/components/DashboardOverview.jsx", "w") as f:
    f.write(content)
