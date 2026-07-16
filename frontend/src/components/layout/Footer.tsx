export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-400">
        &copy; {new Date().getFullYear()} 在线书店 — 全栈学习项目
      </div>
    </footer>
  );
}
