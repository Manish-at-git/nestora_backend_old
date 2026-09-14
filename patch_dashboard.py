with open("../frontend/src/components/DashboardOverview.jsx", "r") as f:
    content = f.read()

# Add activeCommentPoll
content = content.replace(
    'const [activeCommentEvent, setActiveCommentEvent] = useState(null);',
    'const [activeCommentEvent, setActiveCommentEvent] = useState(null);\n  const [activeCommentPoll, setActiveCommentPoll] = useState(null);'
)

# Add poll like logic in toggleLike
content = content.replace(
    "const endpoint = type === 'event' ? `/events/${id}/like` : `/announcements/${id}/like`;",
    "const endpoint = type === 'poll' ? `/polls/${id}/like` : type === 'event' ? `/events/${id}/like` : `/announcements/${id}/like`;"
)

# Add handlePollVote
handle_vote = """
  const handlePollVote = async (pollId, optionId, isMultipleChoice, currentVotes) => {
    try {
      let newVotes = [...currentVotes];
      if (isMultipleChoice) {
        if (newVotes.includes(optionId)) {
          newVotes = newVotes.filter(id => id !== optionId);
        } else {
          newVotes.push(optionId);
        }
      } else {
        newVotes = [optionId];
      }
      
      await api.post(`/polls/${pollId}/vote`, { option_ids: newVotes });
      fetchTimeline(0);
      toast.success("Vote recorded successfully");
    } catch (err) {
      toast.error("Failed to submit vote");
    }
  };
"""
content = content.replace(
    "const handleRSVP = async (meetingId, status) => {",
    handle_vote + "\n  const handleRSVP = async (meetingId, status) => {"
)

# Add rendering logic for poll
poll_renderer = """
    if (item.item_type === 'poll') {
      const isExpired = item.end_date && new Date(item.end_date) < new Date();
      const hasVoted = item.my_votes && item.my_votes.length > 0;
      const showResults = isExpired || hasVoted;

      return (
        <div key={`p-${item.id}`} className="bg-white border border-slate-200 rounded-2xl shadow-sm mb-6 overflow-hidden">
          <div className="bg-indigo-50 px-6 py-4 border-b border-indigo-100 flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-700 font-semibold text-sm tracking-wide uppercase">
              <BarChart2 size={16} /> Community Poll
            </div>
            {isExpired ? (
              <span className="bg-slate-200 text-slate-700 text-xs font-bold px-2.5 py-1 rounded-full">Closed</span>
            ) : (
              <span className="bg-emerald-100 text-emerald-700 text-xs font-bold px-2.5 py-1 rounded-full">Active</span>
            )}
          </div>
          
          <div className="p-6">
            <h3 className="text-xl font-bold text-slate-800 leading-tight mb-2">{item.question}</h3>
            {item.description && (
              <p className="text-slate-600 text-sm mb-5">{item.description}</p>
            )}

            <div className="space-y-3 mb-5">
              {item.options?.map(opt => {
                const isSelected = item.my_votes?.includes(opt.id);
                
                if (showResults) {
                  return (
                    <div key={opt.id} className="relative bg-slate-50 border border-slate-200 rounded-xl overflow-hidden p-3 z-0">
                      <div 
                        className="absolute inset-y-0 left-0 bg-indigo-100 -z-10 transition-all duration-1000 ease-out"
                        style={{ width: `${opt.vote_percentage || 0}%` }}
                      ></div>
                      <div className="flex justify-between items-center text-sm">
                        <span className={`font-medium ${isSelected ? 'text-indigo-700' : 'text-slate-700'}`}>
                          {opt.text} {isSelected && '(Your vote)'}
                        </span>
                        <span className="font-bold text-slate-700">{opt.vote_percentage || 0}%</span>
                      </div>
                    </div>
                  );
                }

                return (
                  <button
                    key={opt.id}
                    onClick={() => handlePollVote(item.id, opt.id, item.is_multiple_choice, item.my_votes || [])}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all flex items-center gap-3 ${
                      isSelected 
                        ? 'border-indigo-600 bg-indigo-50' 
                        : 'border-slate-200 bg-white hover:border-indigo-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className={`w-5 h-5 rounded-${item.is_multiple_choice ? 'md' : 'full'} border-2 flex items-center justify-center ${
                      isSelected ? 'border-indigo-600 bg-indigo-600' : 'border-slate-300'
                    }`}>
                      {isSelected && <Check size={14} className="text-white" />}
                    </div>
                    <span className={`text-sm ${isSelected ? 'text-indigo-900 font-semibold' : 'text-slate-700'}`}>
                      {opt.text}
                    </span>
                  </button>
                );
              })}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <div className="flex gap-4">
                <button 
                  onClick={() => toggleLike(item.id, item.user_has_liked, 'poll')}
                  className={`flex items-center gap-1.5 text-sm font-medium transition-colors ${item.user_has_liked ? 'text-red-500' : 'text-slate-500 hover:text-red-500'}`}
                >
                  <Heart size={18} className={item.user_has_liked ? 'fill-current' : ''} /> {item.like_count || 0}
                </button>
                <button 
                  onClick={() => setActiveCommentPoll(item.id)}
                  className="flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-blue-500 transition-colors"
                >
                  <MessageCircle size={18} /> {item.comment_count || 0}
                </button>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                <span>{formatDate(item.created_at)} - by {item.created_by_name || 'Admin'}</span>
                {!isExpired && item.end_date && (
                  <span className="ml-2 pl-2 border-l border-slate-200 text-indigo-500">
                    Ends {new Date(item.end_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }
"""
content = content.replace(
    "if (item.item_type === 'event') {",
    poll_renderer + "\n    if (item.item_type === 'event') {"
)

# Also need to import BarChart2, Check
if "BarChart2" not in content:
    content = content.replace("import { Megaphone", "import { BarChart2, Check, Megaphone")
elif "Check" not in content:
    content = content.replace("import { Megaphone", "import { Check, Megaphone")

with open("../frontend/src/components/DashboardOverview.jsx", "w") as f:
    f.write(content)
print("Patched DashboardOverview.jsx")
