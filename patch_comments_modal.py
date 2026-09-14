with open("../frontend/src/components/DashboardOverview.jsx", "r") as f:
    content = f.read()

poll_modal = """
      <CommentsModal
        isOpen={!!activeCommentPoll}
        onClose={() => {
          setActiveCommentPoll(null);
          fetchTimeline(0); 
        }}
        itemId={activeCommentPoll}
        itemType="poll"
      />
"""

content = content.replace(
    '        itemType="event"\n      />\n    </div>',
    '        itemType="event"\n      />\n      ' + poll_modal + '\n    </div>'
)

with open("../frontend/src/components/DashboardOverview.jsx", "w") as f:
    f.write(content)

