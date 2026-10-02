const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex justify-center md:justify-start">
            <p className="text-base text-gray-500 font-semibold">
              AI Resume Screening System
            </p>
          </div>
          <div className="mt-4 md:mt-0 md:order-1 flex justify-center text-sm text-gray-400">
            <p>
              Privacy notice: Your resume is processed locally and not shared with external services.
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex justify-center">
            <p className="text-base text-gray-400">
              &copy; {currentYear} All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
